import json

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect

MAX_DEPTH = 3  # static/js/modules/comments.js MAX_DEPTH와 같다
MAX_COMMENT_LENGTH = 3000  # templates/components/comments.html maxlength와 같다


def _fk(reply_model) -> str:
    return "board" if hasattr(reply_model, "board_id") else "post"


def _pk_or_none(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if 0 < number < 2**63 else None


def _valid_comment(comment) -> bool:
    return isinstance(comment, str) and bool(comment.strip()) and len(comment) <= MAX_COMMENT_LENGTH


class ReplyCreateMixin:
    """댓글 생성 폼 POST.

    활성 글에만, 부모는 같은 글의 댓글만. depth·group은 서버가 정한다. 하위 클래스는 reply_model·detail_url_name만 정한다.
    """

    reply_model = None
    detail_url_name = None

    def get(self, request, pk):
        return redirect(self.detail_url_name, pk)

    def post(self, request, pk):
        comment = request.POST.get("comment", "")
        if not comment.strip():
            return redirect(self.detail_url_name, pk)
        if not _valid_comment(comment):
            return HttpResponseBadRequest()

        fk = _fk(self.reply_model)
        post_model = self.reply_model._meta.get_field(fk).related_model
        parent_value = request.POST.get("parent")

        with transaction.atomic():
            # 글 행을 잠가 group 번호와 reply_count를 순서대로 올린다. 삭제·숨김 글은 404(phase3 D1-A).
            post = get_object_or_404(post_model.activate_objects.get_data().select_for_update(), pk=pk)
            updates = {"reply_count": F("reply_count") + 1}
            if parent_value:
                parent_pk = _pk_or_none(parent_value)
                parent = parent_pk and self.reply_model.objects.filter(pk=parent_pk, **{fk: post}).first()
                if not parent:
                    return HttpResponseBadRequest()
                group, depth = parent.group, min(parent.depth + 1, MAX_DEPTH)
            else:
                parent, depth = None, 0
                group = post.last_group_num + 1
                updates["last_group_num"] = group

            self.reply_model.objects.create(
                author=request.user, comment=comment, depth=depth, group=group, parent=parent, **{fk: post}
            )
            post_model.objects.filter(pk=pk).update(**updates)

        return redirect(self.detail_url_name, pk)


class ReplyUpdateMixin:
    """댓글 수정 JSON POST {comment} (ADR-004·005). 응답 {"message"}는 화면 JS 계약이라 그대로 둔다."""

    reply_model = None

    def post(self, request, pk, reply_pk):
        try:
            content = json.loads(request.body)
        except ValueError:  # JSONDecodeError, UnicodeDecodeError
            return HttpResponseBadRequest()
        if not isinstance(content, dict) or "comment" not in content:
            return HttpResponseBadRequest()

        reply = get_object_or_404(self.reply_model, pk=reply_pk, **{_fk(self.reply_model): pk})
        if request.user != reply.author:
            raise PermissionDenied()

        comment = content["comment"]
        if comment is None:
            return JsonResponse({"message": "Reply note updated"})
        if not _valid_comment(comment):
            return HttpResponseBadRequest()

        reply.comment = comment
        reply.save()
        return JsonResponse({"message": "Reply updated"})
