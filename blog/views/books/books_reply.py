import json
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, View

from common.mixin.views.reply_list import ReplyListJsonMixin

from ...models.blog import BooksPost
from ...models.blog_reply import BooksPostReply

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class BooksReplyListJsonView(ReplyListJsonMixin, View):
    reply_model = BooksPostReply


class BooksReplyCreateJsonView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        return redirect("blog:books_detail", kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        author = self.request.user
        comment = self.request.POST.get("comment")
        depth = self.request.POST.get("depth")
        parent_pk = self.request.POST.get("parent")

        if not comment:
            return redirect("blog:books_detail", kwargs.get("pk"))

        if parent_pk:
            parent = BooksPostReply.objects.get(pk=parent_pk)
        else:
            parent = None

        if parent:
            group = parent.group
            post = get_object_or_404(BooksPost, pk=kwargs.get("pk"))
        else:
            with transaction.atomic():
                BooksPost.objects.select_for_update().filter(
                    pk=kwargs.get("pk")
                ).update(last_group_num=F("last_group_num") + 1)
                post = get_object_or_404(BooksPost, pk=kwargs.get("pk"))
            group = post.last_group_num

        with transaction.atomic():
            BooksPostReply.objects.create(
                author=author,
                comment=comment,
                depth=depth,
                group=group,
                parent=parent,
                post=post,
            )
            BooksPost.objects.select_for_update().filter(pk=kwargs.get("pk")).update(
                reply_count=F("reply_count") + 1
            )

        return redirect("blog:books_detail", kwargs.get("pk"))


class BooksReplyUpdateJsonView(LoginRequiredMixin, View):

    def post(self, request, pk, reply_pk):
        content = json.loads(request.body.decode("utf-8"))
        comment = content["comment"]

        reply = get_object_or_404(BooksPostReply, pk=reply_pk)
        if self.request.user != reply.author:
            raise PermissionDenied()

        if comment is None:
            message = "Reply note updated"
        else:
            reply.comment = comment
            reply.save()

            message = "Reply updated"

        context = {"message": message}

        return JsonResponse(context, safe=True)


class BooksReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = BooksPostReply
    pk_url_kwarg = "reply_pk"
    login_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()

        if self.request.user != self.object.author:
            raise PermissionDenied()

        self.post_pk = self.object.post.pk

        return super().form_valid(None)

    def get_success_url(self):
        return reverse_lazy("blog:books_detail", kwargs={"pk": self.post_pk})
