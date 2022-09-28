import logging
from django.views.generic import TemplateView

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

