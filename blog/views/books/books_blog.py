import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from common.mixin.views.post_detail import BlogPostDetailMixin

from ...models.blog import BooksPost
from .books_forms import BooksForm

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class BooksListView(ListView):
    model = BooksPost
    template_name = "blog/blog_list.html"
    paginate_by = 10
    paginate_orphans = 1  # if last page has 1 item, it will add in last page.
    context_object_name = "board"

    def get_queryset(self):
        return BooksPost.activate_objects.get_data().select_related('author')


class BooksDetailView(BlogPostDetailMixin, DetailView):
    model = BooksPost
    template_name = "blog/books/books_detail.html"


class BooksCreateView(LoginRequiredMixin, CreateView):
    model = BooksPost
    template_name = "blog/books/books_edit.html"
    success_url = reverse_lazy("blog:books_list")
    form_class = BooksForm
    login_url = reverse_lazy("users:login")

    def form_valid(self, form):
        data = form.save(commit=False)
        data.author = self.request.user
        data.table_name = self.model.__name__
        data.save()

        data.tag_save(form.cleaned_data["tag_set"])

        return super().form_valid(form)


class BooksUpdateView(LoginRequiredMixin, UpdateView):
    model = BooksPost
    pk_url_kwarg = "pk"
    form_class = BooksForm
    template_name = "blog/books/books_update.html"
    login_url = reverse_lazy("users:login")

    def get_success_url(self):
        return reverse_lazy("blog:books_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()
        data = form.save(commit=False)
        data.save()

        data.tag_save(form.cleaned_data["tag_set"])

        return super().form_valid(form)


class BooksDeleteView(LoginRequiredMixin, View):
    model = BooksPost
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("blog:books_list")
    login_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # 객체를 가져오고, 없으면 404 에러 발생
        post = get_object_or_404(self.model, id=kwargs.get("pk"))

        # 권한 확인
        if self.request.user != post.author:
            raise PermissionDenied()

        # 캐시 삭제
        # 객체 삭제 처리
        post.is_deleted = True
        post.save()

        return redirect(self.success_url)


class BooksLikeJsonView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(BooksPost, pk=pk)

        with transaction.atomic():
            post_like = post.like_user_set.select_for_update().filter(
                pk=self.request.user.pk
            )

            if post_like:  # there are field data already, not created
                message = "Like canceled"
                if post.like_count != 0:
                    BooksPost.objects.filter(pk=pk).update(
                        like_count=F("like_count") - 1
                    )
                    post.like_user_set.remove(self.request.user)
            else:
                message = "Like"
                BooksPost.objects.filter(pk=pk).update(like_count=F("like_count") + 1)
                post.like_user_set.add(self.request.user)

        post = BooksPost.objects.get(pk=pk)  # get latest post information

        context = {"like_count": post.like_count, "message": message}

        return JsonResponse(context, safe=True)


class BooksVisitJsonView(View):
    def get(self, request, pk):
        with transaction.atomic():
            BooksPost.objects.filter(pk=pk).update(visit_count=F("visit_count") + 1)
            message = "visit count updated"

        context = {"message": message}

        return JsonResponse(context, safe=True)
