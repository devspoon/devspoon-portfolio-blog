import logging
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.http import Http404

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Avg, Q
from isort import file
from ...models.boards import InterestingOpenSourcePost
from .opensource_forms import OpenSourceForm

logger = logging.getLogger(__name__)


class OpenSourceListView(ListView):
    model = InterestingOpenSourcePost
    template_name = 'opensource/opensource_list.html'
    paginate_by = 2
    paginate_orphans = 1 # if last page has 1 item, it will add in last page.
    context_object_name = 'board'

    # def get_queryset(self):
    #     return Review.objects.filter(user=self.request.user).all()


class OpenSourceDetailView(DetailView):
    model = InterestingOpenSourcePost
    template_name = 'opensource/opensource_detail.html'
    context_object_name = 'board'

    # def get_object(self):
    #     id_ = self.kwargs.get("pk")
    #     return get_object_or_404(Board, id=id_)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # args = {"board": self.kwargs.get("pk"), "is_deleted": False}
        # context["comments"] = Comment.objects.filter(**args)
        temp_queryset = InterestingOpenSourcePost.objects.filter(Q(pk=context['board'].pk-1) | Q(pk=context['board'].pk+1))
        context['pre_board'] = temp_queryset[0]

        if temp_queryset.count() == 2 :
            context['next_board'] = temp_queryset[1]

        else :
            context['next_board'] = ''

        return context


class OpenSourceCreateView(LoginRequiredMixin, CreateView):
    model = InterestingOpenSourcePost
    template_name = 'opensource/opensource_edit.html'
    success_url = reverse_lazy('blog:index')
    form_class = OpenSourceForm
    # login_url = reverse_lazy('login')

    def form_valid(self, form):
        data = form.save(commit=False)
        data.author = self.request.user
        data.save()

        return super().form_valid(form)


class OpenSourceUpdateView(LoginRequiredMixin, UpdateView):
    model = InterestingOpenSourcePost
    pk_url_kwarg = 'pk'
    form_class = OpenSourceForm
    template_name = 'opensource/opensource_update.html'
    login_url = reverse_lazy('users:login')

    def get_success_url(self):
        return reverse_lazy('blog:opensource_update', kwargs={'pk': self.object.pk})

    # def form_valid(self, form):
    #     review = self.get_object()
    #     if review.user != self.request.user:
    #         raise PermissionDenied()
    #     return super().form_valid(form)


class OpenSourceDeleteView(LoginRequiredMixin, DeleteView):
    model = InterestingOpenSourcePost
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('blog:opensource_list')
    login_url = reverse_lazy('users:login')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()
        #if self.request.user != self.object.user:
        #    raise PermissionDenied()
        return super().form_valid(None)