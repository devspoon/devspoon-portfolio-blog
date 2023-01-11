import logging
from django.views.generic import TemplateView, View
from home.views.service.search import Search
from django.http import Http404

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


class PrivacyPolicyView(TemplateView):
    template_name = 'pages/privacy-policy.html'


class TermsOfServiceView(TemplateView):
    template_name = 'pages/terms-of-service.html'


class SearchView(TemplateView, Search):
    template_name = 'base/search_result_board_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        page_number = self.request.GET.get('page', '1')
        keyword = self.request.GET.get('keyword')
        tag = self.request.GET.get('tag')

        if not tag and not keyword:
            raise Http404("Keyword or tag is essentials")

        if tag:
            return self.queryset_tag_search(tag, page_number, self.paginate_by)

        if keyword:
            return self.queryset_keyword_search(keyword, page_number, self.paginate_by)
