import datetime
import json
import logging
import re
from email.policy import default
from signal import default_int_handler

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, UpdateView, View

from board.models.board import Visiter
from board.models.board_reply import VisiterReply

logger = logging.getLogger(getattr(settings, "BOARD_LOGGER", "django"))


def make_list_by_paginator(paginator, pages):
    number = pages.number
    num_pages = paginator.num_pages

    return [{"number": number, "num_pages": num_pages}]


class VisiterReplyListJsonView(View):
    the_number_of_replies = 10

    def get(self, request, pk):
        post = VisiterReply.objects.filter(board=pk).select_related("author")
        paginator = Paginator(post, self.the_number_of_replies)
        page = request.GET.get("page", 1)

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
                    "post": str(context.board.pk),
                    "created_at": context.created_at.strftime("%Y-%m-%d %I:%M:%S %p"),
                    "thumbnail": str(context.author.photo_thumbnail.url),
                    "user_auth": str(context.author) == str(request.user.username),
                },
                pages.object_list,
            )
        )

        results = pagination_info + replies

        return JsonResponse(results, safe=False)


class VisiterReplyCreateJsonView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        return redirect("board:visiter_detail", kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        author = self.request.user
        comment = self.request.POST.get("comment")
        depth = self.request.POST.get("depth")
        parent_pk = self.request.POST.get("parent")

        if not comment:
            return redirect("board:visiter_detail", kwargs.get("pk"))

        if parent_pk:
            parent = VisiterReply.objects.get(pk=parent_pk)
        else:
            parent = None

        if parent:
            group = parent.group
            post = get_object_or_404(Visiter, pk=kwargs.get("pk"))
        else:
            with transaction.atomic():
                Visiter.objects.select_for_update().filter(pk=kwargs.get("pk")).update(
                    last_group_num=F("last_group_num") + 1
                )
                post = get_object_or_404(Visiter, pk=kwargs.get("pk"))
            group = post.last_group_num

        with transaction.atomic():
            VisiterReply.objects.create(
                author=author,
                comment=comment,
                depth=depth,
                group=group,
                parent=parent,
                board=post,
            )
            Visiter.objects.select_for_update().filter(pk=kwargs.get("pk")).update(
                reply_count=F("reply_count") + 1
            )

        return redirect("board:visiter_detail", kwargs.get("pk"))


class VisiterReplyUpdateJsonView(LoginRequiredMixin, View):
    def post(self, request, pk, reply_pk):
        content = json.loads(request.body.decode("utf-8"))
        comment = content["comment"]

        reply = get_object_or_404(VisiterReply, pk=reply_pk)
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


class VisiterReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = VisiterReply
    pk_url_kwarg = "reply_pk"
    login_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()

        if self.request.user != self.object.author:
            raise PermissionDenied()

        self.post_pk = self.object.board.pk
        return super().form_valid(None)

    def get_success_url(self):
        return reverse_lazy("board:visiter_detail", kwargs={"pk": self.post_pk})
