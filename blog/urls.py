from django.urls import path, include
from . import views

from .views.index import IndexView

app_name = "blog"

main_patterns = [
    path('', IndexView.as_view(),name='index'),
]

search_patterns = []

blog_patterns = [
    # path('', video_views.swipe),
    # path('show/', video_views.show, name='show'),
    # path('detail/<int:id>', video_views.detail, name='detail'),
    # path('like/', video_views.like, name='like'),
]

books_patterns = []
error_patterns = []
opensource_patterns = []
portfolio_patterns = []
project_patterns = []
study_patterns = []

urlpatterns = [
    path('', include(main_patterns)),
    path('search/', include(search_patterns)),
    path('blog/', include(blog_patterns)),
    path('books/', include(books_patterns)),
    path('error/', include(error_patterns)),
    path('opensource/', include(opensource_patterns)),
    path('portfolio/', include(portfolio_patterns)),
    path('project/', include(project_patterns)),
    path('study/', include(study_patterns)),
]