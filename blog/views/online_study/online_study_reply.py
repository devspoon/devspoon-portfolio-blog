import json
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, View

from common.components.django_redis_cache_components import (
    dredis_cache_check_key,
    dredis_cache_delete,
    dredis_cache_get,
    dredis_cache_set,
)

from ...models.blog import OnlineStudyPost
from ...models.blog_reply import OnlineStudyPostReply

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


def make_list_by_paginator(paginator, pages):
    number = pages.number
    num_pages = paginator.num_pages

    return [{"number": number, "num_pages": num_pages}]


class OnlineStudyReplyListJsonView(View):
    the_number_of_replies = 10
    cache_prefix = "blog:OnlineStudyReply"

    def get(self, request, pk):
        page = request.GET.get("page", 1)

        check_cached_key = dredis_cache_check_key(
            self.cache_prefix,
            pk,
            page,
        )
        if check_cached_key:
            logger.debug(f"called redis cache - {self.__class__.__name__}")
            results = dredis_cache_get(
                self.cache_prefix,
                pk,
                page,
            )
        else:
            post = OnlineStudyPostReply.objects.filter(post=pk).select_related("author")
            paginator = Paginator(post, self.the_number_of_replies)

            pages = paginator.get_page(page)

            pagination_info = make_list_by_paginator(paginator, pages)

            replies = list(
                map(
                    lambda context: {
                        "pk": context.pk,
                        "author": str(context.author),
                        "comment": context.comment,
                        "depth": context.depth,
                        "group": context.group,
                        "parent": str(context.parent_id),
                        "post": str(context.post_id),
                        "created_at": context.created_at.strftime(
                            "%Y-%m-%d %I:%M:%S %p"
                        ),
                        "thumbnail": str(context.author.photo_thumbnail.url),
                        "author_id": context.author_id,
                    },
                    pages.object_list,
                )
            )

            results = pagination_info + replies
            caching_data = {}
            caching_data[page] = results
            logger.debug(f"called database - {self.__class__.__name__}")
            if caching_data:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} caching_data exists"
                )
                dredis_cache_set(
                    self.cache_prefix,
                    pk,
                    **caching_data,
                )
            else:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} caching_data not exists"
                )

        # 요청자마다 다른 값은 공유 캐시에 넣지 않는다(C-1). 작성자 판정은 사용자 id로 한다.
        # author_id가 없는 옛 형식 캐시는 모두 False가 되어 버튼이 잘못 보이지 않는다.
        user_pk = request.user.pk  # 비로그인이면 None
        for reply in results[1:]:
            author_id = reply.pop("author_id", None)
            reply["user_auth"] = user_pk is not None and author_id == user_pk

        logger.debug(f"final context : {results}")

        return JsonResponse(results, safe=False)


class OnlineStudyReplyCreateJsonView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:login")
    cache_prefix = "blog:OnlineStudyReply"

    def get(self, request, *args, **kwargs):
        return redirect("blog:online_study_detail", kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        author = self.request.user
        comment = self.request.POST.get("comment")
        depth = self.request.POST.get("depth")
        parent_pk = self.request.POST.get("parent")

        if not comment:
            return redirect("blog:online_study_detail", kwargs.get("pk"))

        if parent_pk:
            parent = OnlineStudyPostReply.objects.get(pk=parent_pk)
        else:
            parent = None

        if parent:
            group = parent.group
            post = get_object_or_404(OnlineStudyPost, pk=kwargs.get("pk"))
        else:
            with transaction.atomic():
                OnlineStudyPost.objects.select_for_update().filter(
                    pk=kwargs.get("pk")
                ).update(last_group_num=F("last_group_num") + 1)
                post = get_object_or_404(OnlineStudyPost, pk=kwargs.get("pk"))
            group = post.last_group_num

        with transaction.atomic():
            OnlineStudyPostReply.objects.create(
                author=author,
                comment=comment,
                depth=depth,
                group=group,
                parent=parent,
                post=post,
            )
            OnlineStudyPost.objects.select_for_update().filter(
                pk=kwargs.get("pk")
            ).update(reply_count=F("reply_count") + 1)

        dredis_cache_delete(self.cache_prefix, kwargs.get("pk"))

        return redirect("blog:online_study_detail", kwargs.get("pk"))


class OnlineStudyReplyUpdateJsonView(LoginRequiredMixin, View):
    cache_prefix = "blog:OnlineStudyReply"

    def post(self, request, pk, reply_pk):
        content = json.loads(request.body.decode("utf-8"))
        comment = content["comment"]

        reply = get_object_or_404(OnlineStudyPostReply, pk=reply_pk)
        if self.request.user != reply.author:
            raise PermissionDenied()

        if comment is None:
            message = "Reply note updated"
        else:
            reply.comment = comment
            reply.save()

            message = "Reply updated"

        context = {"message": message}

        dredis_cache_delete(self.cache_prefix, pk)

        return JsonResponse(context, safe=True)


class OnlineStudyReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = OnlineStudyPostReply
    pk_url_kwarg = "reply_pk"
    login_url = reverse_lazy("users:login")
    cache_prefix = "blog:OnlineStudyReply"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()

        if self.request.user != self.object.author:
            raise PermissionDenied()

        self.post_pk = self.object.post.pk

        dredis_cache_delete(self.cache_prefix, kwargs.get("pk"))
        return super().form_valid(None)

    def get_success_url(self):
        return reverse_lazy("blog:online_study_detail", kwargs={"pk": self.post_pk})
