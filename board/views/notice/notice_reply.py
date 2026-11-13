import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import DeleteView, View

from board.models.board_reply import NoticeReply
from common.mixin.views.reply_list import ReplyListJsonMixin
from common.mixin.views.reply_write import ReplyCreateMixin, ReplyUpdateMixin

logger = logging.getLogger(getattr(settings, "BOARD_LOGGER", "django"))


class NoticeReplyListJsonView(ReplyListJsonMixin, View):
    reply_model = NoticeReply


class NoticeReplyCreateJsonView(LoginRequiredMixin, ReplyCreateMixin, View):
    login_url = reverse_lazy("users:login")
    reply_model = NoticeReply
    detail_url_name = "board:notice_detail"


class NoticeReplyUpdateJsonView(LoginRequiredMixin, ReplyUpdateMixin, View):
    reply_model = NoticeReply


class NoticeReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = NoticeReply
    pk_url_kwarg = "reply_pk"
    login_url = reverse_lazy("users:login")

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()

        if self.request.user != self.object.author:
            raise PermissionDenied()

        self.post_pk = self.object.board.pk

        return super().form_valid(None)

    def get_success_url(self):
        return reverse_lazy("board:notice_detail", kwargs={"pk": self.post_pk})
