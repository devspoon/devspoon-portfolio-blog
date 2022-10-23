import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import View, CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView
from django.http import Http404

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import F, Q
from django.db import transaction

from ...models.board import Reactivation
from .reactivation_forms import ReactivationForm

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ReactivationListView(ListView):
    model = Reactivation
    template_name = 'board/board_list.html'
    paginate_by = 10
    paginate_orphans = 1 # if last page has 1 item, it will add in last page.
    context_object_name = 'board'

    def get_queryset(self):
        return Reactivation.activate_objects.get_data()


class ReactivationDetailView(DetailView):
    model = Reactivation
    template_name = 'board/reactivation/reactivation_detail.html'
    context_object_name = 'board'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_auth'] = self.get_object().author == self.request.user

        return context


class ReactivationCreateView(LoginRequiredMixin, CreateView):
    model = Reactivation
    template_name = 'board/reactivation/reactivation_edit.html'
    success_url = reverse_lazy('board:reactivation')
    form_class = ReactivationForm
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        data = form.save(commit=False)
        data.author = self.request.user
        data.table_name = self.model.__name__
        data.save()

        return super().form_valid(form)

class ReactivationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reactivation
    pk_url_kwarg = 'pk'
    form_class = ReactivationForm
    template_name = 'board/reactivation/reactivation_update.html'
    login_url = reverse_lazy('users:login')

    def get_success_url(self):
        return reverse_lazy('board:reactivation_update', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()

        return super().form_valid(form)


class ReactivationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reactivation
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('board:reactivation_list')
    login_url = reverse_lazy('users:login')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()
        if self.request.user != self.object.author:
            raise PermissionDenied()

        return super().form_valid(None)


class ReactivationVisitJsonView(View):

    def get(self, request, pk):

        with transaction.atomic():
            Reactivation.objects.filter(pk=pk).update(visit_count=F('visit_count') + 1)
            message = "visit count updated"

        context = {'message': message}

        return JsonResponse(context, safe=True)