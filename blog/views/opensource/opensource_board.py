import logging
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.http import Http404

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Avg
from isort import file
from ...models.boards import InterestingOpenSourcePost
from .opensource_forms import OpenSourceForm

logger = logging.getLogger(__name__)


class OpenSourceListView(ListView):
    model = InterestingOpenSourcePost
    template_name = 'opensource/opensource_list.html' 
    paginate_by = 5
    paginate_orphans = 1
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

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     args = {"board": self.kwargs.get("pk"), "is_deleted": False}
    #     context["comments"] = Comment.objects.filter(**args)
    #     return context


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
        # file1 = self.request.FILES.getlist('file1')
        # print('file1 : ',file1)
        # if file1 :
        #     PostFiles.objects.create(file=file1)
            
        # file2 = self.request.FILES.getlist('file2')
        # if file2 :
        #     PostFiles.objects.create(file=file2)            
        
        return super().form_valid(form)
    

class OpenSourceUpdateView(LoginRequiredMixin, UpdateView):
    ...
    # model = InterestingOpenSourcePost
    # pk_url_kwarg = 'review_id'
    # fields = ['comment', 'ratings']
    # template_name = 'opensource/update.html'
    # success_url = reverse_lazy('review-history')
    # login_url = reverse_lazy('login')

    # def form_valid(self, form):
    #     review = self.get_object()
    #     if review.user != self.request.user:
    #         raise PermissionDenied()
    #     return super().form_valid(form)
    

class OpenSourceDeleteView(LoginRequiredMixin, DeleteView):
    ...
    # model = InterestingOpenSourcePost
    # pk_url_kwarg = 'review_id'
    # success_url = reverse_lazy('review-history')
    # login_url = reverse_lazy('login')

    # def get(self, request, *args, **kwargs):
    #     return self.post(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     self.object = super().get_object()
    #     if self.request.user != self.object.user:
    #         raise PermissionDenied()
    #     return super().form_valid(None)