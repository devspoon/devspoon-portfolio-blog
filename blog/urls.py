from django.urls import include, path

from blog.views.blog.blog_blog import (
    BlogCreateView,
    BlogDeleteView,
    BlogDetailView,
    BlogLikeJsonView,
    BlogListView,
    BlogUpdateView,
    BlogVisitJsonView,
)
from blog.views.blog.blog_reply import (
    BlogReplyCreateJsonView,
    BlogReplyDeleteView,
    BlogReplyListJsonView,
    BlogReplyUpdateJsonView,
)
from blog.views.books.books_blog import (
    BooksCreateView,
    BooksDeleteView,
    BooksDetailView,
    BooksLikeJsonView,
    BooksListView,
    BooksUpdateView,
    BooksVisitJsonView,
)
from blog.views.books.books_reply import (
    BooksReplyCreateJsonView,
    BooksReplyDeleteView,
    BooksReplyListJsonView,
    BooksReplyUpdateJsonView,
)
from blog.views.online_study.online_study_blog import (
    OnlineStudyCreateView,
    OnlineStudyDeleteView,
    OnlineStudyDetailView,
    OnlineStudyLikeJsonView,
    OnlineStudyListView,
    OnlineStudyUpdateView,
    OnlineStudyVisitJsonView,
)
from blog.views.online_study.online_study_reply import (
    OnlineStudyReplyCreateJsonView,
    OnlineStudyReplyDeleteView,
    OnlineStudyReplyListJsonView,
    OnlineStudyReplyUpdateJsonView,
)
from blog.views.opensource.opensource_blog import (
    OpenSourceCreateView,
    OpenSourceDeleteView,
    OpenSourceDetailView,
    OpenSourceLikeJsonView,
    OpenSourceListView,
    OpenSourceUpdateView,
    OpenSourceVisitJsonView,
)
from blog.views.opensource.opensource_reply import (
    OpenSourceReplyCreateJsonView,
    OpenSourceReplyDeleteView,
    OpenSourceReplyListJsonView,
    OpenSourceReplyUpdateJsonView,
)
from blog.views.project.project_blog import (
    ProjectCreateView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectLikeJsonView,
    ProjectListView,
    ProjectUpdateView,
    ProjectVisitJsonView,
)
from blog.views.project.project_reply import (
    ProjectReplyCreateJsonView,
    ProjectReplyDeleteView,
    ProjectReplyListJsonView,
    ProjectReplyUpdateJsonView,
)

app_name = "blog"

blog_patterns = [
    path("", BlogListView.as_view(), name="blog_list"),
    path("create/", BlogCreateView.as_view(), name="blog_create"),
    path("update/<int:pk>/", BlogUpdateView.as_view(), name="blog_update"),
    path("delete/<int:pk>/", BlogDeleteView.as_view(), name="blog_delete"),
    path("like/json/<int:pk>/", BlogLikeJsonView.as_view(), name="blog_like"),
    path("detail/<int:pk>/", BlogDetailView.as_view(), name="blog_detail"),
    path(
        "detail/<int:pk>/reply/json/",
        BlogReplyListJsonView.as_view(),
        name="blog_reply_list",
    ),
    path(
        "detail/<int:pk>/reply/json/create/",
        BlogReplyCreateJsonView.as_view(),
        name="blog_reply_create",
    ),
    path(
        "detail/<int:pk>/reply/json/update/<int:reply_pk>/",
        BlogReplyUpdateJsonView.as_view(),
        name="blog_reply_update",
    ),
    path(
        "detail/<int:pk>/reply/delete/<int:reply_pk>/",
        BlogReplyDeleteView.as_view(),
        name="blog_reply_delete",
    ),
    path("detail/<int:pk>/visit/json/", BlogVisitJsonView.as_view(), name="blog_visit"),
]

books_patterns = [
    path("", BooksListView.as_view(), name="books_list"),
    path("create/", BooksCreateView.as_view(), name="books_create"),
    path("update/<int:pk>/", BooksUpdateView.as_view(), name="books_update"),
    path("delete/<int:pk>/", BooksDeleteView.as_view(), name="books_delete"),
    path("like/json/<int:pk>/", BooksLikeJsonView.as_view(), name="books_like"),
    path("detail/<int:pk>/", BooksDetailView.as_view(), name="books_detail"),
    path(
        "detail/<int:pk>/reply/json/",
        BooksReplyListJsonView.as_view(),
        name="books_reply_list",
    ),
    path(
        "detail/<int:pk>/reply/json/create/",
        BooksReplyCreateJsonView.as_view(),
        name="books_reply_create",
    ),
    path(
        "detail/<int:pk>/reply/json/update/<int:reply_pk>/",
        BooksReplyUpdateJsonView.as_view(),
        name="books_reply_update",
    ),
    path(
        "detail/<int:pk>/reply/delete/<int:reply_pk>/",
        BooksReplyDeleteView.as_view(),
        name="books_reply_delete",
    ),
    path(
        "detail/<int:pk>/visit/json/", BooksVisitJsonView.as_view(), name="books_visit"
    ),
]

opensource_patterns = [
    path("", OpenSourceListView.as_view(), name="opensource_list"),
    path("create/", OpenSourceCreateView.as_view(), name="opensource_create"),
    path("update/<int:pk>/", OpenSourceUpdateView.as_view(), name="opensource_update"),
    path("delete/<int:pk>/", OpenSourceDeleteView.as_view(), name="opensource_delete"),
    path(
        "like/json/<int:pk>/", OpenSourceLikeJsonView.as_view(), name="opensource_like"
    ),
    path("detail/<int:pk>/", OpenSourceDetailView.as_view(), name="opensource_detail"),
    path(
        "detail/<int:pk>/reply/json/",
        OpenSourceReplyListJsonView.as_view(),
        name="opensource_reply_list",
    ),
    path(
        "detail/<int:pk>/reply/json/create/",
        OpenSourceReplyCreateJsonView.as_view(),
        name="opensource_reply_create",
    ),
    path(
        "detail/<int:pk>/reply/json/update/<int:reply_pk>/",
        OpenSourceReplyUpdateJsonView.as_view(),
        name="opensource_reply_update",
    ),
    path(
        "detail/<int:pk>/reply/delete/<int:reply_pk>/",
        OpenSourceReplyDeleteView.as_view(),
        name="opensource_reply_delete",
    ),
    path(
        "detail/<int:pk>/visit/json/",
        OpenSourceVisitJsonView.as_view(),
        name="opensource_visit",
    ),
]

project_patterns = [
    path("", ProjectListView.as_view(), name="project_list"),
    path("create/", ProjectCreateView.as_view(), name="project_create"),
    path("update/<int:pk>/", ProjectUpdateView.as_view(), name="project_update"),
    path("delete/<int:pk>/", ProjectDeleteView.as_view(), name="project_delete"),
    path("like/json/<int:pk>/", ProjectLikeJsonView.as_view(), name="project_like"),
    path("detail/<int:pk>/", ProjectDetailView.as_view(), name="project_detail"),
    path(
        "detail/<int:pk>/reply/json/",
        ProjectReplyListJsonView.as_view(),
        name="project_reply_list",
    ),
    path(
        "detail/<int:pk>/reply/json/create/",
        ProjectReplyCreateJsonView.as_view(),
        name="project_reply_create",
    ),
    path(
        "detail/<int:pk>/reply/json/update/<int:reply_pk>/",
        ProjectReplyUpdateJsonView.as_view(),
        name="project_reply_update",
    ),
    path(
        "detail/<int:pk>/reply/delete/<int:reply_pk>/",
        ProjectReplyDeleteView.as_view(),
        name="project_reply_delete",
    ),
    path(
        "detail/<int:pk>/visit/json/",
        ProjectVisitJsonView.as_view(),
        name="project_visit",
    ),
]

online_study_patterns = [
    path("", OnlineStudyListView.as_view(), name="online_study_list"),
    path("create/", OnlineStudyCreateView.as_view(), name="online_study_create"),
    path(
        "update/<int:pk>/", OnlineStudyUpdateView.as_view(), name="online_study_update"
    ),
    path(
        "delete/<int:pk>/", OnlineStudyDeleteView.as_view(), name="online_study_delete"
    ),
    path(
        "like/json/<int:pk>/",
        OnlineStudyLikeJsonView.as_view(),
        name="online_study_like",
    ),
    path(
        "detail/<int:pk>/", OnlineStudyDetailView.as_view(), name="online_study_detail"
    ),
    path(
        "detail/<int:pk>/reply/json/",
        OnlineStudyReplyListJsonView.as_view(),
        name="online_study_reply_list",
    ),
    path(
        "detail/<int:pk>/reply/json/create/",
        OnlineStudyReplyCreateJsonView.as_view(),
        name="online_study_reply_create",
    ),
    path(
        "detail/<int:pk>/reply/json/update/<int:reply_pk>/",
        OnlineStudyReplyUpdateJsonView.as_view(),
        name="online_study_reply_update",
    ),
    path(
        "detail/<int:pk>/reply/delete/<int:reply_pk>/",
        OnlineStudyReplyDeleteView.as_view(),
        name="online_study_reply_delete",
    ),
    path(
        "detail/<int:pk>/visit/json/",
        OnlineStudyVisitJsonView.as_view(),
        name="online_study_visit",
    ),
]

urlpatterns = [
    path("blog/", include(blog_patterns)),
    path("books/", include(books_patterns)),
    path("opensource/", include(opensource_patterns)),
    path("project/", include(project_patterns)),
    path("onlinestudy/", include(online_study_patterns)),
]
