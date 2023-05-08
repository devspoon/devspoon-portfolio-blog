import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import F
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

# from ..models.boards import OpenSourcePost, Tag
# from .opensource_forms import OpenSourceForm


logger = logging.getLogger(getattr(settings, "BOARD_LOGGER", "django"))


class VisiterListView(TemplateView):
    template_name = "board/board_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
