from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse

from common.components.django_redis_cache_components import CACHE_TTL, reply_page_key


def page_number(value) -> int:
    """?page 값을 1 이상의 정수로. 없거나 잘못된 값은 1(phase3 F-008)."""
    try:
        return max(int(value), 1)
    except (TypeError, ValueError):
        return 1


class ReplyListJsonMixin:
    """글 하나의 댓글 목록 JSON (docs/crp/groups/phase3-cache-redesign, ADR-004·008).

    응답: [{"number", "num_pages"}, 댓글, ...]. 하위 클래스는 reply_model만 정한다.
    """

    reply_model = None
    the_number_of_replies = 10

    def get(self, request, pk):
        fk = "board" if hasattr(self.reply_model, "board_id") else "post"
        post_model = self.reply_model._meta.get_field(fk).related_model
        page = page_number(request.GET.get("page"))
        key = reply_page_key(post_model, pk, page)

        results = cache.get(key)
        if results is None:
            replies = self.reply_model.objects.filter(**{fk: pk}).select_related("author")
            pages = Paginator(replies, self.the_number_of_replies).get_page(page)
            results = [{"number": pages.number, "num_pages": pages.paginator.num_pages}] + [
                {
                    "pk": reply.pk,
                    "author": str(reply.author),
                    "comment": reply.comment,
                    "depth": reply.depth,
                    "group": reply.group,
                    "parent": str(reply.parent_id),
                    "post": str(getattr(reply, f"{fk}_id")),
                    "created_at": reply.created_at.strftime("%Y-%m-%d %I:%M:%S %p"),
                    "thumbnail": str(reply.author.photo_thumbnail.url),
                    "author_id": reply.author_id,
                }
                for reply in pages.object_list
            ]
            # 범위 밖 페이지는 Paginator가 마지막 페이지로 맞춘 결과라 그 페이지 번호로 캐시하지 않는다.
            if pages.number == page:
                cache.set(key, results, timeout=CACHE_TTL)

        # 요청자마다 다른 값은 캐시에 넣지 않는다(phase1 C-1). 작성자 판정은 사용자 id로 한다.
        user_pk = request.user.pk  # 비로그인이면 None
        for reply in results[1:]:
            author_id = reply.pop("author_id", None)
            reply["user_auth"] = user_pk is not None and author_id == user_pk

        return JsonResponse(results, safe=False)
