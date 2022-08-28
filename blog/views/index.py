import logging
from django.utils import timezone
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import Http404

from django.db.models import Avg
from ..models.default import MainMenu

from .service.search import BlogSearch

logger = logging.getLogger(__name__)

# logger.info("info")
# logger.warning("warning")
# logger.debug("debug")
# logger.error("error")

# Create your views here.

class IndexView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

