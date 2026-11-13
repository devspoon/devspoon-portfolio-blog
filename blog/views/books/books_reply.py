import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import DeleteView, View

from common.mixin.views.reply_list import ReplyListJsonMixin
from common.mixin.views.reply_write import ReplyCreateMixin, ReplyUpdateMixin

from ...models.blog_reply import BooksPostReply

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class BooksReplyListJsonView(ReplyListJsonMixin, View):
    reply_model = BooksPostReply


class BooksReplyCreateJsonView(LoginRequiredMixin, ReplyCreateMixin, View):
    login_url = reverse_lazy("users:login")
    reply_model = BooksPostReply
    detail_url_name = "blog:books_detail"


class BooksReplyUpdateJsonView(LoginRequiredMixin, ReplyUpdateMixin, View):
    reply_model = BooksPostReply


class BooksReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = BooksPostReply
    pk_url_kwarg = "reply_pk"
    login_url = reverse_lazy("users:login")

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()

        if self.request.user != self.object.author:
            raise PermissionDenied()

        self.post_pk = self.object.post.pk

        return super().form_valid(None)

    def get_success_url(self):
        return reverse_lazy("blog:books_detail", kwargs={"pk": self.post_pk})
