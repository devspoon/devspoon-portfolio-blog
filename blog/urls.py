from django.urls import path, include

from .views.index import IndexView
from blog.views.opensource.opensource_board import OpenSourceListView, OpenSourceDetailView, OpenSourceCreateView, OpenSourceUpdateView, OpenSourceDeleteView, OpenSourceLikeJsonView

app_name = "blog"

main_patterns = [
    path('', IndexView.as_view(),name='index'),
    # path('search/', video_views.like, name='like'),
    # path('tag/', video_views.like, name='like'),
]

search_patterns = []

blog_patterns = [
    # path('', video_views.swipe),
    # path('show/', video_views.show, name='show'),
    # path('detail/<int:pk>', video_views.detail, name='detail'),
    # path('like/', video_views.like, name='like'),
]

books_patterns = []
error_patterns = []
opensource_patterns = [
    path('', OpenSourceListView.as_view(),name='opensource_list'),
    path('detail/<int:pk>/', OpenSourceDetailView.as_view(), name='opensource_detail'),
    path('create/', OpenSourceCreateView.as_view(), name='opensource_create'),
    path('update/<int:pk>/', OpenSourceUpdateView.as_view(), name='opensource_update'),
    path('delete/<int:pk>/', OpenSourceDeleteView.as_view(), name='opensource_delete'),
    path('like/json/<int:pk>/', OpenSourceLikeJsonView.as_view(),name='opensource_like'),
]
portfolio_patterns = []
project_patterns = []
study_patterns = []
online_patterns = []

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
    path('online/', include(online_patterns)),
]