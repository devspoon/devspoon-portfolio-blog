import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import View, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.http import Http404

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import F, Q
from django.db import transaction
from isort import file

from ...models.blog import BooksPost
from .books_forms import BooksForm

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class BooksListView(ListView):
    model = BooksPost
    template_name = 'blog/books/books_list.html'
    paginate_by = 10
    paginate_orphans = 1 # if last page has 1 item, it will add in last page.
    context_object_name = 'board'

    def get_queryset(self):
        return BooksPost.objects.filter(Q(is_hidden=False) and Q(is_deleted=False))


class BooksDetailView(DetailView):
    model = BooksPost
    template_name = 'blog/books/books_detail.html'
    context_object_name = 'board'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pre_temp_queryset = BooksPost.objects.filter(pk__lt=context['board'].pk).order_by('-pk').first()
        next_temp_queryset = BooksPost.objects.filter(pk__gt=context['board'].pk).order_by('pk').first()

        if not pre_temp_queryset :
            context['pre_board'] = ''
        else :
            context['pre_board'] = pre_temp_queryset

        if not pre_temp_queryset :
            context['next_board'] = ''
        else :
            context['next_board'] = next_temp_queryset

        context['like_state'] = BooksPost.objects.filter(pk=self.kwargs.get('pk')).first().like_user_set.filter(pk=self.request.user.pk).exists()

        context['user_auth'] = self.get_object().author == self.request.user

        return context


class BooksCreateView(LoginRequiredMixin, CreateView):
    model = BooksPost
    template_name = 'blog/books/books_edit.html'
    success_url = reverse_lazy('blog:books_list')
    form_class = BooksForm
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        data = form.save(commit=False)
        data.author = self.request.user
        data.table_name = self.model.__name__
        data.save()

        data.tag_save(form.cleaned_data['tags'])

        return super().form_valid(form)


class BooksUpdateView(LoginRequiredMixin, UpdateView):
    model = BooksPost
    pk_url_kwarg = 'pk'
    form_class = BooksForm
    template_name = 'blog/books/books_update.html'
    login_url = reverse_lazy('users:login')

    def get_success_url(self):
        return reverse_lazy('blog:books_update', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        review = self.get_object()
        if self.request.user != review.author:
            raise PermissionDenied()
        data = form.save(commit=False)
        data.save()

        data.tag_save(form.cleaned_data['tags'])


        return super().form_valid(form)


class BooksDeleteView(LoginRequiredMixin, DeleteView):
    model = BooksPost
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('blog:books_list')
    login_url = reverse_lazy('users:login')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = super().get_object()
        if self.request.user != self.object.author:
           raise PermissionDenied()
        return super().form_valid(None)


class BooksLikeJsonView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(BooksPost, pk=pk)

        with transaction.atomic():
            post_like = post.like_user_set.select_for_update().filter(pk=self.request.user.pk)

            if post_like: # there are field data already, not created
                message = "Like canceled"
                if post.like_count != 0:
                    BooksPost.objects.filter(pk=pk).update(like_count=F('like_count') - 1)
                    post.like_user_set.remove(self.request.user)
            else:
                message = "Like"
                BooksPost.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
                post.like_user_set.add(self.request.user)

        post = BooksPost.objects.get(pk=pk) # get latest post information

        context = {'like_count': post.like_count,
                'message': message}

        return JsonResponse(context, safe=True)


class BooksVisitJsonView(View):

    def get(self, request, pk):

        with transaction.atomic():
            BooksPost.objects.filter(pk=pk).update(visit_count=F('visit_count') + 1)
            message = "visit count updated"

        context = {'message': message}

        return JsonResponse(context, safe=True)