import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from common.components.django_redis_cache_components import (
    dredis_cache_check_key,
    dredis_cache_delete,
    dredis_cache_get,
    dredis_cache_set,
)

from ...models.board import Notice
from .notice_forms import NoticeForm

logger = logging.getLogger(getattr(settings, "BOARD_LOGGER", "django"))


class NoticeListView(ListView):
    model = Notice
    template_name = "board/board_list.html"
    paginate_by = 10
    paginate_orphans = 1  # if last page has 1 item, it will add in last page.
    context_object_name = "board"

    def get_queryset(self):
        return Notice.activate_objects.get_data()


class NoticeDetailView(DetailView):
    model = Notice
    template_name = "board/notice/notice_detail.html"
    context_object_name = "board"
    cache_prefix = "board:Notice"

    def get_queryset(self):
        check_cached_key = dredis_cache_check_key(
            self.cache_prefix,
            self.kwargs.get("pk"),
            "get_queryset",
        )
        if check_cached_key:
            queryset = dredis_cache_get(
                self.cache_prefix,
                self.kwargs.get("pk"),
                "get_queryset",
            )
        else:
            queryset = super().get_queryset()
            dredis_cache_set(
                self.cache_prefix,
                self.kwargs.get("pk"),
                get_queryset=queryset,
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        check_cached_key = dredis_cache_check_key(
            self.cache_prefix, self.kwargs.get("pk"), "user_auth"
        )
        if check_cached_key:
            queryset = dredis_cache_get(
                self.cache_prefix,
                self.kwargs.get("pk"),
            )
            context.update(queryset)
        else:
            context["user_auth"] = self.request.user
            caching_data = context.copy()

            [caching_data.pop(x, None) for x in ["object", "board", "view"]]
            dredis_cache_set(
                self.cache_prefix,
                self.kwargs.get("pk"),
                **caching_data,
            )

        logger.debug(f"final context : {context}")

        return context


class NoticeCreateView(LoginRequiredMixin, CreateView):
    model = Notice
    template_name = "board/notice/notice_edit.html"
    success_url = reverse_lazy("board:notice_list")
    form_class = NoticeForm
    login_url = reverse_lazy("users:login")

    def form_valid(self, form):
        data = form.save(commit=False)
        data.author = self.request.user
        data.table_name = self.model.__name__
        data.save()

        return super().form_valid(form)


class NoticeUpdateView(LoginRequiredMixin, UpdateView):
    model = Notice
    pk_url_kwarg = "pk"
    form_class = NoticeForm
    template_name = "board/notice/notice_update.html"
    login_url = reverse_lazy("users:login")
    cache_prefix = "board:Notice"

    def get_success_url(self):
        return reverse_lazy("board:notice_update", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()

        dredis_cache_delete(
            self.cache_prefix,
            self.kwargs.get("pk"),
        )

        return super().form_valid(form)


class NoticeDeleteView(LoginRequiredMixin, DeleteView):
    model = Notice
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("board:notice_list")
    login_url = reverse_lazy("users:login")
    cache_prefix = "board:Notice"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()
        if self.request.user != self.object.author:
            raise PermissionDenied()
        dredis_cache_delete(
            self.cache_prefix,
            self.kwargs.get("pk"),
        )

        return super().form_valid(None)


class NoticeVisitJsonView(View):
    def get(self, request, pk):
        with transaction.atomic():
            Notice.objects.filter(pk=pk).update(visit_count=F("visit_count") + 1)
            message = "visit count updated"

        context = {"message": message}

        return JsonResponse(context, safe=True)
