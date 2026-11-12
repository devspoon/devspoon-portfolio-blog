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

from ...models.blog import OpenSourcePost
from .opensource_forms import OpenSourceForm

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class OpenSourceListView(ListView):
    model = OpenSourcePost
    template_name = "blog/blog_list.html"
    paginate_by = 10
    paginate_orphans = 1  # if last page has 1 item, it will add in last page.
    context_object_name = "board"

    def get_queryset(self):
        return OpenSourcePost.activate_objects.get_data().select_related('author')


class OpenSourceDetailView(BlogPostDetailMixin, DetailView):
    model = OpenSourcePost
    template_name = "blog/opensource/opensource_detail.html"


class OpenSourceCreateView(LoginRequiredMixin, CreateView):
    model = OpenSourcePost
    template_name = "blog/opensource/opensource_edit.html"
    success_url = reverse_lazy("blog:opensource_list")
    form_class = OpenSourceForm
    login_url = reverse_lazy("users:login")

    def form_valid(self, form):
        data = form.save(commit=False)
        data.author = self.request.user
        data.table_name = self.model.__name__
        data.save()

        data.tag_save(form.cleaned_data["tag_set"])

        return super().form_valid(form)


class OpenSourceUpdateView(LoginRequiredMixin, UpdateView):
    model = OpenSourcePost
    pk_url_kwarg = "pk"
    form_class = OpenSourceForm
    template_name = "blog/opensource/opensource_update.html"
    login_url = reverse_lazy("users:login")

    def get_success_url(self):
        return reverse_lazy("blog:opensource_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()
        data = form.save(commit=False)
        data.save()

        data.tag_save(form.cleaned_data["tag_set"])

        return super().form_valid(form)


class OpenSourceDeleteView(LoginRequiredMixin, View):
    model = OpenSourcePost
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("blog:opensource_list")
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


class OpenSourceLikeJsonView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(OpenSourcePost, pk=pk)

        with transaction.atomic():
            post_like = post.like_user_set.select_for_update().filter(
                pk=self.request.user.pk
            )

            if post_like:  # there are field data already, not created
                message = "Like canceled"
                if post.like_count != 0:
                    OpenSourcePost.objects.filter(pk=pk).update(
                        like_count=F("like_count") - 1
                    )
                    post.like_user_set.remove(self.request.user)
            else:
                message = "Like"
                OpenSourcePost.objects.filter(pk=pk).update(
                    like_count=F("like_count") + 1
                )
                post.like_user_set.add(self.request.user)

        post = OpenSourcePost.objects.get(pk=pk)  # get latest post information

        context = {"like_count": post.like_count, "message": message}

        return JsonResponse(context, safe=True)


class OpenSourceVisitJsonView(View):
    def get(self, request, pk):
        with transaction.atomic():
            OpenSourcePost.objects.filter(pk=pk).update(
                visit_count=F("visit_count") + 1
            )
            message = "visit count updated"

        context = {"message": message}

        return JsonResponse(context, safe=True)
