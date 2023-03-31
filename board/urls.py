from django.urls import include, path

from .views.notice.notice_board import (
    NoticeCreateView,
    NoticeDeleteView,
    NoticeDetailView,
    NoticeListView,
    NoticeUpdateView,
    NoticeVisitJsonView,
)
from .views.notice.notice_reply import (
    NoticeReplyCreateJsonView,
    NoticeReplyDeleteView,
    NoticeReplyListJsonView,
    NoticeReplyUpdateJsonView,
)
from .views.reactivation.reactivation_board import (
    ReactivationCreateView,
    ReactivationDeleteView,
    ReactivationDetailView,
    ReactivationListView,
    ReactivationUpdateView,
    ReactivationVisitJsonView,
)
from .views.reactivation.reactivation_reply import (
    ReactivationReplyCreateJsonView,
    ReactivationReplyDeleteView,
    ReactivationReplyListJsonView,
    ReactivationReplyUpdateJsonView,
)
from .views.visiter.visiter_board import (
    VisiterCreateView,
    VisiterDeleteView,
    VisiterDetailView,
    VisiterListView,
    VisiterUpdateView,
    VisiterVisitJsonView,
)
from .views.visiter.visiter_reply import (
    VisiterReplyCreateJsonView,
    VisiterReplyDeleteView,
    VisiterReplyListJsonView,
    VisiterReplyUpdateJsonView,
)

app_name = "board"

notice_patterns = [
    path("", NoticeListView.as_view(), name="notice_list"),
    path("write/", NoticeCreateView.as_view(), name="notice_write"),
    path("update/<int:pk>/", NoticeUpdateView.as_view(), name="notice_update"),
    path("delete/<int:pk>/", NoticeDeleteView.as_view(), name="notice_delete"),
    path("detail/<int:pk>/", NoticeDetailView.as_view(), name="notice_detail"),
    path(
        "detail/<int:pk>/reply/json/",
        NoticeReplyListJsonView.as_view(),
        name="notice_reply_list",
    ),
    path(
        "detail/<int:pk>/reply/json/create/",
        NoticeReplyCreateJsonView.as_view(),
        name="notice_reply_create",
    ),
    path(
        "detail/<int:pk>/reply/json/update/<int:reply_pk>/",
        NoticeReplyUpdateJsonView.as_view(),
        name="notice_reply_update",
    ),
    path(
        "detail/<int:pk>/reply/delete/<int:reply_pk>/",
        NoticeReplyDeleteView.as_view(),
        name="notice_reply_delete",
    ),
    path(
        "detail/<int:pk>/visit/json/",
        NoticeVisitJsonView.as_view(),
        name="notice_visit",
    ),
]

reactivation_patterns = [
    path("", ReactivationListView.as_view(), name="reactivation_list"),
    path("write/", ReactivationCreateView.as_view(), name="reactivation_write"),
    path(
        "update/<int:pk>/", ReactivationUpdateView.as_view(), name="reactivation_update"
    ),
    path(
        "delete/<int:pk>/", ReactivationDeleteView.as_view(), name="reactivation_delete"
    ),
    path(
        "detail/<int:pk>/", ReactivationDetailView.as_view(), name="reactivation_detail"
    ),
    path(
        "detail/<int:pk>/reply/json/",
        ReactivationReplyListJsonView.as_view(),
        name="reactivation_reply_list",
    ),
    path(
        "detail/<int:pk>/reply/json/create/",
        ReactivationReplyCreateJsonView.as_view(),
        name="reactivation_reply_create",
    ),
    path(
        "detail/<int:pk>/reply/json/update/<int:reply_pk>/",
        ReactivationReplyUpdateJsonView.as_view(),
        name="reactivation_reply_update",
    ),
    path(
        "detail/<int:pk>/reply/delete/<int:reply_pk>/",
        ReactivationReplyDeleteView.as_view(),
        name="reactivation_reply_delete",
    ),
    path(
        "detail/<int:pk>/visit/json/",
        ReactivationVisitJsonView.as_view(),
        name="reactivation_visit",
    ),
]

visiter_patterns = [
    path("", VisiterListView.as_view(), name="visiter_list"),
    path("write/", VisiterCreateView.as_view(), name="visiter_write"),
    path("update/<int:pk>/", VisiterUpdateView.as_view(), name="visiter_update"),
    path("delete/<int:pk>/", VisiterDeleteView.as_view(), name="visiter_delete"),
    path("detail/<int:pk>/", VisiterDetailView.as_view(), name="visiter_detail"),
    path(
        "detail/<int:pk>/reply/json/",
        VisiterReplyListJsonView.as_view(),
        name="visiter_reply_list",
    ),
    path(
        "detail/<int:pk>/reply/json/create/",
        VisiterReplyCreateJsonView.as_view(),
        name="visiter_reply_create",
    ),
    path(
        "detail/<int:pk>/reply/json/update/<int:reply_pk>/",
        VisiterReplyUpdateJsonView.as_view(),
        name="visiter_reply_update",
    ),
    path(
        "detail/<int:pk>/reply/delete/<int:reply_pk>/",
        VisiterReplyDeleteView.as_view(),
        name="visiter_reply_delete",
    ),
    path(
        "detail/<int:pk>/visit/json/",
        VisiterVisitJsonView.as_view(),
        name="visiter_visit",
    ),
]


urlpatterns = [
    path("notice/", include(notice_patterns)),
    path("reactivation/", include(reactivation_patterns)),
    path("visiter/", include(visiter_patterns)),
]
