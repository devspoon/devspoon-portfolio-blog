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
    dredis_cache_check_key, dredis_cache_delete, dredis_cache_get,
    dredis_cache_set)

from ...models.blog import BlogPost
from ...models.blog_reply import BlogPostReply

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


def make_list_by_paginator(paginator, pages):
    number = pages.number
    num_pages = paginator.num_pages

    return [{"number": number, "num_pages": num_pages}]


class BlogReplyListJsonView(View):
    the_number_of_replies = 10
    cache_prefix = "blog:BlogReply"

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
            post = BlogPostReply.objects.filter(post=pk).select_related("author")
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
                        "post": str(context.post.pk),
                        "created_at": context.created_at.strftime(
                            "%Y-%m-%d %I:%M:%S %p"
                        ),
                        "thumbnail": str(context.author.photo_thumbnail.url),
                        "user_auth": str(context.author) == str(request.user.username),
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

        logger.debug(f"final context : {results}")
        return JsonResponse(results, safe=False)


class BlogReplyCreateJsonView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:login")
    cache_prefix = "blog:BlogReply"

    def get(self, request, *args, **kwargs):
        return redirect("blog:blog_detail", kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        author = self.request.user
        comment = self.request.POST.get("comment")
        depth = self.request.POST.get("depth")
        parent_pk = self.request.POST.get("parent")

        if not comment:
            return redirect("blog:blog_detail", kwargs.get("pk"))

        if parent_pk:
            parent = BlogPostReply.objects.get(pk=parent_pk)
        else:
            parent = None

        if parent:
            group = parent.group
            post = get_object_or_404(BlogPost, pk=kwargs.get("pk"))
        else:
            with transaction.atomic():
                BlogPost.objects.select_for_update().filter(pk=kwargs.get("pk")).update(
                    last_group_num=F("last_group_num") + 1
                )
                post = get_object_or_404(BlogPost, pk=kwargs.get("pk"))
            group = post.last_group_num

        with transaction.atomic():
            BlogPostReply.objects.create(
                author=author,
                comment=comment,
                depth=depth,
                group=group,
                parent=parent,
                post=post,
            )
            BlogPost.objects.select_for_update().filter(pk=kwargs.get("pk")).update(
                reply_count=F("reply_count") + 1
            )

        dredis_cache_delete(
            self.cache_prefix,
            kwargs.get("pk"),
        )

        return redirect("blog:blog_detail", kwargs.get("pk"))


class BlogReplyUpdateJsonView(LoginRequiredMixin, View):
    cache_prefix = "blog:BlogReply"

    def get(self, request, *args, **kwargs):
        return redirect("blog:blog_reply_update", kwargs.get("reply_pk"))

    def post(self, request, pk, reply_pk):
        content = json.loads(request.body.decode("utf-8"))
        comment = content["comment"]

        reply = get_object_or_404(BlogPostReply, pk=reply_pk)
        if self.request.user != reply.author:
            raise PermissionDenied()

        if comment is None:
            message = "Reply note updated"
        else:
            reply.comment = comment
            reply.save()

            message = "Reply updated"

        context = {"message": message}

        dredis_cache_delete(
            self.cache_prefix,
            pk,
        )

        return JsonResponse(context, safe=True)


class BlogReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = BlogPostReply
    pk_url_kwarg = "reply_pk"
    login_url = reverse_lazy("users:login")
    cache_prefix = "blog:BlogReply"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()

        if self.request.user != self.object.author:
            raise PermissionDenied()

        self.post_pk = self.object.post.pk

        dredis_cache_delete(
            self.cache_prefix,
            kwargs.get("pk"),
        )
        return super().form_valid(None)

    def get_success_url(self):
        return reverse_lazy("blog:blog_detail", kwargs={"pk": self.post_pk})
