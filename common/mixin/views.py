from django.contrib.auth.mixins import UserPassesTestMixin


VIEWER_KEYS = ("user_auth", "like_state")


def apply_viewer_state(request, context):
    """Viewer-specific detail state, computed per request (never cached per post — ADR-017)."""
    board, user = context["board"], request.user
    context["user_auth"] = user.is_authenticated and board.author_id == user.pk
    if hasattr(board, "like_user_set"):
        context["like_state"] = user.is_authenticated and board.like_user_set.filter(pk=user.pk).exists()
    return context


class StaffRequiredMixin(UserPassesTestMixin):
    """Place after LoginRequiredMixin: anonymous -> login page, logged-in non-staff -> 403."""

    def test_func(self):
        return self.request.user.is_staff
