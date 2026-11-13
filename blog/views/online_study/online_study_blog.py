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
    DetailView,
    ListView,
    UpdateView,
    View,
)

from common.mixin.views.post_detail import BlogPostDetailMixin

from ...models.blog import OnlineStudyPost
from .online_study_forms import OnlineStudyForm

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class OnlineStudyListView(ListView):
    model = OnlineStudyPost
    template_name = "blog/blog_list.html"
    paginate_by = 10
    paginate_orphans = 1  # if last page has 1 item, it will add in last page.
    context_object_name = "board"

    def get_queryset(self):
        return OnlineStudyPost.activate_objects.get_data().select_related('author')


class OnlineStudyDetailView(BlogPostDetailMixin, DetailView):
    model = OnlineStudyPost
    template_name = "blog/online_study/online_study_detail.html"


class OnlineStudyCreateView(LoginRequiredMixin, CreateView):
    model = OnlineStudyPost
    template_name = "blog/online_study/online_study_edit.html"
    success_url = reverse_lazy("blog:online_study_list")
    form_class = OnlineStudyForm
    login_url = reverse_lazy("users:login")

    def form_valid(self, form):
        data = form.save(commit=False)
        data.author = self.request.user
        data.table_name = self.model.__name__
        data.save()

        data.tag_save(form.cleaned_data["tag_set"])

        return super().form_valid(form)


class OnlineStudyUpdateView(LoginRequiredMixin, UpdateView):
    model = OnlineStudyPost
    pk_url_kwarg = "pk"
    form_class = OnlineStudyForm
    template_name = "blog/online_study/online_study_update.html"
    login_url = reverse_lazy("users:login")

    def get_success_url(self):
        return reverse_lazy("blog:online_study_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()
        data = form.save(commit=False)
        data.save()

        data.tag_save(form.cleaned_data["tag_set"])

        return super().form_valid(form)


class OnlineStudyDeleteView(LoginRequiredMixin, View):
    model = OnlineStudyPost
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("blog:online_study_list")
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


class OnlineStudyLikeJsonView(LoginRequiredMixin, View):
    def get(self, request, pk):
        with transaction.atomic():
            # 글 행을 잠가 같은 글의 토글을 순서대로 처리한다. 좋아요 행은 없을 수 있어 잠금 대상이 못 된다(phase4 F-003).
            post = get_object_or_404(OnlineStudyPost.objects.select_for_update(), pk=pk)
            # 라우터가 읽기를 replica로 보내므로, 잠근 트랜잭션 안의 읽기는 default에서 한다.
            if post.like_user_set.using("default").filter(pk=request.user.pk).exists():
                post.like_user_set.remove(request.user)
                message = "Like canceled"
            else:
                post.like_user_set.add(request.user)
                message = "Like"
            # 증감 대신 실제 행 수로 맞춘다. 옛 중복으로 어긋난 값도 여기서 바로잡힌다.
            like_count = post.like_user_set.using("default").count()
            OnlineStudyPost.objects.filter(pk=pk).update(like_count=like_count)

        return JsonResponse({"like_count": like_count, "message": message}, safe=True)


class OnlineStudyVisitJsonView(View):
    def get(self, request, pk):
        with transaction.atomic():
            OnlineStudyPost.objects.filter(pk=pk).update(
                visit_count=F("visit_count") + 1
            )
            message = "visit count updated"

        context = {"message": message}

        return JsonResponse(context, safe=True)
