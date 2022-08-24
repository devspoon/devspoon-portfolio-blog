import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

from django import forms
from django.views.generic import View, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from ...models.reply import OpenSourcePostReply

from ...views.opensource.opensource_reply_forms import ReplyCreateForm, ReplyUpdateForm


class OpenSourceReplyCreateView(LoginRequiredMixin, View):

    login_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        return redirect('blog:opensource_detail', kwargs.get('pk'))

    def post(self, request, *args, **kwargs):
        comment = self.request.POST.get('comment')
        if not comment :
            return redirect('blog:opensource_detail', kwargs.get('pk'))


        return redirect('blog:opensource_detail', kwargs.get('pk'))



class OpenSourceReplyUpdateView(LoginRequiredMixin, UpdateView):

    model = OpenSourcePostReply
    pk_url_kwarg = 'pk'
    form_class = ReplyUpdateForm
    login_url = reverse_lazy('users:login')

    def get(self, request, *args, **kwargs):
        return redirect('blog:opensource_detail', kwargs.get('pk'))

    def get_success_url(self):
        return reverse_lazy('blog:opensource_detail', kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()
        return super().form_valid(form)

class OpenSourceReplyDeleteView(LoginRequiredMixin, DeleteView):

    model = OpenSourcePostReply
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('blog:opensource_list')
    login_url = reverse_lazy('users:login')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()
        if self.request.user != self.object.author:
           raise PermissionDenied()
        return super().form_valid(None)