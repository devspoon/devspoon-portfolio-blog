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

    # def get_context_data(self, **kwargs):
        #logging.info(f"session info : {__class__.__name__} {self.request.user.is_authenticated} {timezone.now()} {self.request.session.get_expiry_age()} {self.request.session.get_expiry_date()}")
        # pass
        # recommendations = Recommendation.objects.filter(visible=True).order_by('sort')\
        #                       .select_related('restaurant').all()[:4]
        # latest = Restaurant.objects.order_by('-created_at')[:4]
        # hottest = Restaurant.objects.annotate(average_ratings=Avg('review__ratings'))\
        #     .filter(average_ratings__gte=0).order_by('-average_ratings')[:4]

        # logger.info("recommendations: %d", len(recommendations))
        # return {
        #     'recommendations': recommendations,
        #     'latest': latest,
        #     'hottest': hottest
        # }

# class SearchView(TemplateView, RestaurantSearch):
#     template_name = 'main/search.html'

#     def get_context_data(self, **kwargs):
#         page_number = self.request.GET.get('page', '1')
#         keyword = self.request.GET.get('keyword')
#         category_id = self.request.GET.get('category')

#         weekday = self.request.GET.get('weekday')
#         start_time = self.request.GET.get('start')
#         end_time = self.request.GET.get('end')

#         return self.search(keyword, category_id, weekday, start_time, end_time, page_number)


# class SearchJsonView(View, RestaurantSearch):
#     def get(self, request):
#         page_number = self.request.GET.get('page', '1')
#         keyword = self.request.GET.get('keyword')
#         category_id = self.request.GET.get('category')

#         weekday = self.request.GET.get('weekday')
#         start_time = self.request.GET.get('start')
#         end_time = self.request.GET.get('end')

#         data = self.search(keyword, category_id, weekday, start_time, end_time, page_number)

#         # for restaurant in data.get('paging'):
#         #     results.add {
#         #         "id": restaurant.id,
#         #         "name": restaurant.name,
#         #         "address": restaurant.address,
#         #         "image": str(restaurant.main_image.image),
#         #         "category_name": restaurant.category.name
#         #     }

#         results = list(
#             map(lambda restaurant: {
#                 "id": restaurant.id,
#                 "name": restaurant.name,
#                 "address": restaurant.address,
#                 "image": str(restaurant.main_image.image),
#                 "category_name": restaurant.category.name
#             }, data.get('paging'))
#         )

#         return JsonResponse(results, safe=False)