import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from common.components.django_redis_cache_components import (
    dredis_cache_check_key,
    dredis_cache_delete,
    dredis_cache_get,
    dredis_cache_set,
)
from common.decorators.cache import index_cache_clean

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


class OpenSourceDetailView(DetailView):
    model = OpenSourcePost
    template_name = "blog/opensource/opensource_detail.html"
    context_object_name = "board"
    cache_prefix = "blog:OpenSource"

    def get_queryset(self):
        check_cached_key = dredis_cache_check_key(
            self.cache_prefix,
            self.kwargs.get("pk"),
            "get_queryset",
        )
        if check_cached_key:
            logger.debug(f"called redis cache - {self.__class__.__name__}")
            queryset = dredis_cache_get(
                self.cache_prefix,
                self.kwargs.get("pk"),
                "get_queryset",
            )
        else:
            queryset = super().get_queryset()
            logger.debug(f"called database - {self.__class__.__name__}")
            if queryset.exists():
                logger.debug(f"redis cache - {self.__class__.__name__} queryset.exists")
                dredis_cache_set(
                    self.cache_prefix,
                    self.kwargs.get("pk"),
                    get_queryset=queryset,
                )
            else:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} queryset not exists"
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        check_cached_key = dredis_cache_check_key(
            self.cache_prefix, self.kwargs.get("pk"), "user_auth"
        )
        if check_cached_key:
            logger.debug(f"called redis cache - {self.__class__.__name__}")
            queryset = dredis_cache_get(
                self.cache_prefix,
                self.kwargs.get("pk"),
            )
            context.update(queryset)
        else:
            pre_temp_queryset = (
                OpenSourcePost.objects.filter(pk__lt=context["board"].pk)
                .order_by("-pk")
                .first()
            )
            next_temp_queryset = (
                OpenSourcePost.objects.filter(pk__gt=context["board"].pk)
                .order_by("pk")
                .first()
            )

            context["pre_board"] = pre_temp_queryset if pre_temp_queryset else ""
            context["next_board"] = next_temp_queryset if next_temp_queryset else ""

            context["like_state"] = (
                OpenSourcePost.objects.filter(pk=self.kwargs.get("pk"))
                .first()
                .like_user_set.filter(pk=self.request.user.pk)
                .exists()
            )

            context["user_auth"] = self.request.user
            caching_data = context.copy()

            [caching_data.pop(x, None) for x in ["object", "board", "view"]]
            logger.debug(f"called database - {self.__class__.__name__}")
            if caching_data:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} caching_data exists"
                )
                dredis_cache_set(
                    self.cache_prefix,
                    self.kwargs.get("pk"),
                    **caching_data,
                )
            else:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} caching_data not exists"
                )

        logger.debug(f"final context : {context}")
        return context


@method_decorator(index_cache_clean, name="dispatch")
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


@method_decorator(index_cache_clean, name="dispatch")
class OpenSourceUpdateView(LoginRequiredMixin, UpdateView):
    model = OpenSourcePost
    pk_url_kwarg = "pk"
    form_class = OpenSourceForm
    template_name = "blog/opensource/opensource_update.html"
    login_url = reverse_lazy("users:login")
    cache_prefix = "blog:OpenSource"

    def get_success_url(self):
        return reverse_lazy("blog:opensource_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()
        data = form.save(commit=False)
        data.save()

        data.tag_save(form.cleaned_data["tag_set"])

        dredis_cache_delete(
            self.cache_prefix,
            self.kwargs.get("pk"),
        )

        return super().form_valid(form)


@method_decorator(index_cache_clean, name="dispatch")
class OpenSourceDeleteView(LoginRequiredMixin, View):
    model = OpenSourcePost
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("blog:opensource_list")
    login_url = reverse_lazy("users:login")
    cache_prefix = "blog:OpenSource"
    cache_reply_prefix = "blog:OpenSourceReply"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # 객체를 가져오고, 없으면 404 에러 발생
        post = get_object_or_404(self.model, id=kwargs.get("pk"))

        # 권한 확인
        if self.request.user != post.author:
            raise PermissionDenied()

        # 캐시 삭제
        dredis_cache_delete(self.cache_prefix, kwargs.get("pk"))
        dredis_cache_delete(self.cache_reply_prefix, kwargs.get("pk"))

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
