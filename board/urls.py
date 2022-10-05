from django.urls import path, include
from .views.notice.notice_board import NoticeListView, NoticeCreateView, NoticeUpdateView, NoticeDeleteView, NoticeDetailView, NoticeVisitJsonView
from .views.notice.notice_reply import NoticeReplyListJsonView, NoticeReplyCreateJsonView, NoticeReplyUpdateJsonView, NoticeReplyDeleteView

app_name = "board"

notice_patterns = [
    path('', NoticeListView.as_view(), name='notice'),
    path('write/', NoticeCreateView.as_view(), name='notice_write'),
    path('update/<int:pk>/', NoticeUpdateView.as_view(), name='notice_update'),
    path('delete/<int:pk>/', NoticeDeleteView.as_view(), name='notice_delete'),

    path('detail/<int:pk>/', NoticeDetailView.as_view(), name='notice_detail'),

    path('detail/<int:pk>/reply/json/',NoticeReplyListJsonView.as_view(),name='notice_reply_list'),
    path('detail/<int:pk>/reply/json/create/',NoticeReplyCreateJsonView.as_view(),name='notice_reply_create'),
    path('detail/<int:pk>/reply/json/update/<int:reply_pk>/',NoticeReplyUpdateJsonView.as_view(),name='notice_reply_update'),
    path('detail/<int:pk>/reply/delete/<int:reply_pk>/',NoticeReplyDeleteView.as_view(),name='notice_reply_delete'),

    path('detail/<int:pk>/visit/json/',NoticeVisitJsonView.as_view(),name='notice_visit'),
]

# visiter_patterns = [
#     path('visiter/', VisiterListView.as_view(), name='visiter'),
# ]

# reactivation_patterns = [
#     path('reactivation/', VisiterListView.as_view(), name='reactivation'),
# ]

urlpatterns = [
    path('notice/', include(notice_patterns)),
    # path('visiter/', include(visiter_patterns)),
    # path('reactivation/', include(reactivation_patterns)),
]


