import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
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

from ...models.board import Notice
from .notice_forms import NoticeForm

logger = logging.getLogger(getattr(settings, "BOARD_LOGGER", "django"))

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


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

    def get_queryset(self):
        key = "board:NoticeDetailView" + str(self.kwargs.get(self.pk_url_kwarg))
        if key in cache:
            queryset = cache.get(key)
        else:
            queryset = super().get_queryset()
            cache.set(key, queryset, timeout=CACHE_TTL, nx=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_auth"] = self.request.user

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

    def get_success_url(self):
        return reverse_lazy("board:notice_update", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()

        return super().form_valid(form)


class NoticeDeleteView(LoginRequiredMixin, DeleteView):
    model = Notice
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("board:notice_list")
    login_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()
        if self.request.user != self.object.author:
            raise PermissionDenied()
        key = "board:NoticeDetailView" + str(self.kwargs.get(self.pk_url_kwarg))
        cache.delete(key)

        return super().form_valid(None)


class NoticeVisitJsonView(View):
    def get(self, request, pk):
        with transaction.atomic():
            Notice.objects.filter(pk=pk).update(visit_count=F("visit_count") + 1)
            message = "visit count updated"

        context = {"message": message}

        return JsonResponse(context, safe=True)
