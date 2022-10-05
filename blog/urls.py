from django.urls import path, include

from blog.views.opensource.opensource_blog import OpenSourceListView, OpenSourceDetailView, OpenSourceCreateView, OpenSourceUpdateView, OpenSourceDeleteView, OpenSourceLikeJsonView, OpenSourceVisitJsonView
from blog.views.opensource.opensource_reply import OpenSourceReplyCreateJsonView, OpenSourceReplyUpdateJsonView, OpenSourceReplyDeleteView,OpenSourceReplyListJsonView

app_name = "blog"

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
    path('create/', OpenSourceCreateView.as_view(), name='opensource_create'),
    path('update/<int:pk>/', OpenSourceUpdateView.as_view(), name='opensource_update'),
    path('delete/<int:pk>/', OpenSourceDeleteView.as_view(), name='opensource_delete'),
    path('like/json/<int:pk>/', OpenSourceLikeJsonView.as_view(),name='opensource_like'),

    path('detail/<int:pk>/', OpenSourceDetailView.as_view(), name='opensource_detail'),

    path('detail/<int:pk>/reply/json/',OpenSourceReplyListJsonView.as_view(),name='opensource_reply_list'),
    path('detail/<int:pk>/reply/json/create/',OpenSourceReplyCreateJsonView.as_view(),name='opensource_reply_create'),
    path('detail/<int:pk>/reply/json/update/<int:reply_pk>/',OpenSourceReplyUpdateJsonView.as_view(),name='opensource_reply_update'),
    path('detail/<int:pk>/reply/delete/<int:reply_pk>/',OpenSourceReplyDeleteView.as_view(),name='opensource_reply_delete'),

    path('detail/<int:pk>/visit/json/',OpenSourceVisitJsonView.as_view(),name='opensource_visit'),
]
portfolio_patterns = []
project_patterns = []
study_patterns = []
online_patterns = []

urlpatterns = [
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