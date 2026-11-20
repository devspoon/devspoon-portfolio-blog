class PostDetailMixin:
    """글 상세.

    캐시하지 않는다(D2-A): pk 조회라 DB가 충분히 빠르고, 좋아요 수 같은 값이 늘 최신이다.
    삭제·숨김 글은 누구에게나 404다(D1-A). admin에서만 본다.
    """

    context_object_name = "board"

    def get_queryset(self):
        return self.model.activate_objects.get_data().select_related("author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user_auth"] = user.is_authenticated and user.pk == context["board"].author_id
        return context


class BlogPostDetailMixin(PostDetailMixin):
    """블로그 게시판은 이전/다음 글과 좋아요 상태도 보여 준다."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context["board"]
        active = self.model.activate_objects.get_data()
        context["pre_board"] = active.filter(pk__lt=post.pk).order_by("-pk").first() or ""
        context["next_board"] = active.filter(pk__gt=post.pk).order_by("pk").first() or ""
        user = self.request.user
        context["like_state"] = (
            user.is_authenticated and post.like_user_set.filter(pk=user.pk).exists()
        )
        return context
