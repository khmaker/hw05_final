from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.base import View
from django.views.generic.list import ListView

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post


class IndexView(ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'posts/index.html'
    page_kwarg = 'page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = context.pop('page_obj')  # test requirements
        return context


class GroupView(ListView):
    model = Group
    paginate_by = 10
    context_object_name = 'group'
    template_name = 'group.html'
    page_kwarg = 'page'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_object_or_404(self.model,
                                 slug=self.kwargs.get('slug')).posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(self.model,
                                             slug=self.kwargs.get('slug'))
        context['page'] = context.pop('page_obj')  # test requirements

        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'posts/new.html'
    extra_context = {
            'title': 'Новая запись',
            'header': 'Добавление публикации',
            'button': 'Добавить',
            }
    context = {}

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None,
                               files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        self.context['form'] = form
        return render(request, self.template_name, self.context)


class ProfileView(ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'profile.html'
    page_kwarg = 'page'
    user = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.user = request.user
        return super().dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(get_user_model(),
                                   username=self.kwargs.get('username'))
        context['post_count'] = self.model.objects.filter(
                author=author).count()
        context['author'] = author
        context['following'] = Follow.objects.filter(user=self.user,
                                                     author=author).exists()
        context['page'] = context.pop('page_obj')  # test requirements
        return context

    def get_queryset(self):
        author = get_object_or_404(get_user_model(),
                                   username=self.kwargs.get('username'))
        return self.model.objects.filter(author=author).all()


class PostView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    template_name = 'posts/post.html'
    user = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.user = request.user
        return super().dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(get_user_model(),
                                   username=self.kwargs.get('username'))
        context['post_count'] = self.model.objects.filter(
                author=author).count()
        context['author'] = author
        context['following'] = author.follower.filter(user=self.user).exists()
        context['items'] = Comment.objects.filter(post=context['post']).all()
        context['form'] = CommentForm()
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    template_name = 'posts/new.html'
    extra_context = {
            'title': 'Редактировать запись',
            'header': 'Редактирование публикации',
            'button': 'Отредактировать',
            }

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.author != self.request.user:
            return redirect('post', username=self.kwargs['username'],
                            post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post', kwargs={
                'username': self.kwargs['username'],
                'post_id': self.kwargs['post_id']
                })


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = '/'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.author != self.request.user or request.method == 'GET':
            return redirect('post', username=self.kwargs['username'],
                            post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


class AddCommentView(LoginRequiredMixin, DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    template_name = 'posts/post.html'
    user = None
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.user = request.user
        return super().dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(get_user_model(),
                                   username=self.kwargs.get('username'))
        context['post_count'] = self.model.objects.filter(
                author=author).count()
        context['author'] = author
        context['following'] = Follow.objects.filter(user=self.user,
                                                     author=author).exists()
        context['form'] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        comment.save()
        return redirect('post', username=self.kwargs['username'],
                        post_id=self.kwargs['post_id'])


class FollowIndexView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'posts/follow.html'
    page_kwarg = 'page'
    context = {}
    user = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = context.pop('page_obj')  # test requirements
        return context


class ProfileFollowView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        author = get_object_or_404(get_user_model(),
                                   username=self.kwargs['username'])
        if request.user == author:
            return redirect("profile", username=self.kwargs['username'])
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect("profile", username=self.kwargs['username'])


class ProfileUnfollowView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        author = get_object_or_404(get_user_model(),
                                   username=self.kwargs['username'])
        if request.user == author:
            return redirect("profile", username=self.kwargs['username'])
        Follow.objects.get(user=request.user, author=author).delete()
        return redirect("profile", username=self.kwargs['username'])
