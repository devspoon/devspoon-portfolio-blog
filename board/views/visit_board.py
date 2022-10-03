import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import View, CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView
from django.http import Http404

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import F

#from ..models.boards import OpenSourcePost, Tag
#from .opensource_forms import OpenSourceForm

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class VisiterListView(TemplateView):
    template_name = 'board/board_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
