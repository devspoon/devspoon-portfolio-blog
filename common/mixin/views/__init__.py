from django.contrib.auth.mixins import UserPassesTestMixin


class StaffRequiredMixin(UserPassesTestMixin):
    """Place after LoginRequiredMixin: anonymous -> login page, logged-in non-staff -> 403."""

    def test_func(self):
        return self.request.user.is_staff
