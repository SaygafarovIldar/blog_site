from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datetime_safe import datetime
from django.views.generic import DeleteView, UpdateView, ListView

from .forms import LoginForm, RegistrationForm, PostForm, CommentForm
from .models import Category, Post, PostCountViews, Comment, Like, DisLike


# Create your views here.


class HomeListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "blog_app/index.html"


class SearchResults(HomeListView):
    def get_queryset(self):
        query = self.request.GET.get("q")
        # return Post.objects.filter(title__icontains=query)
        return Post.objects.filter(
            Q(title__iregex=query) | Q(content__iregex=query)
        )


# def home_page(request):
#     posts = Post.objects.all()
#     context = {
#         "posts": posts
#     }
#     return render(request, "blog_app/index.html", context)


def contact_page(request):
    return render(request, "blog_app/test.html")


def category_posts(request, category_id):
    category = Category.objects.get(pk=category_id)
    posts = Post.objects.filter(category=category)
    context = {
        "posts": posts
    }
    return render(request, "blog_app/index.html", context)


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    comments = post.comments.filter(post=post)

    try:
        post.dislikes
    except Exception as e:
        print(e)
        DisLike.objects.create(post=post)

    try:
        post.likes
    except Exception as e:
        print(e)
        Like.objects.create(post=post)

    likes_count = post.likes.user.all().count()
    comments_likes_count = sum([comment.likes.user.all().count() for comment in post.comments.all()])
    comments_dislikes_count = sum([comment.dislikes.user.all().count() for comment in post.comments.all()])

    dislikes_count = post.dislikes.user.all().count()

    # если нет активной сессии для юзера сохранить ее
    if not request.session.session_key:
        request.session.save()

    # получаем ключ сессии (cookie)
    session_key = request.session.session_key

    is_viewed = PostCountViews.objects.filter(post=post, session_id=session_key)

    if is_viewed.count() == 0 and str(session_key) != "None":
        views = PostCountViews()
        views.session_id = session_key
        views.post = post
        views.save()

        post.views += 1
        post.save()

    if request.method == "POST":
        form = CommentForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.post = post
            form.author = request.user
            form.save()
            try:
                form.dislikes
            except Exception as e:
                print(e)
                DisLike.objects.create(comment=form)

            try:
                form.likes
            except Exception as e:
                print(e)
                Like.objects.create(comment=form)
            return redirect("post_detail", post.pk)
    else:
        form = CommentForm()

    context = {
        "post": post,
        "form": form,
        "comments": comments,
        "likes_count": likes_count,
        "dislikes_count": dislikes_count,
        "comments_likes_count": comments_likes_count,
        "comments_dislikes_count": comments_dislikes_count
    }
    return render(request, "blog_app/post_detail.html", context)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = LoginForm()
    context = {
        "form": form
    }
    return render(request, "blog_app/login.html", context)


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()  # сохранение данных в моделе User
            return redirect("login")
    else:
        form = RegistrationForm()

    context = {
        "form": form
    }
    return render(request, "blog_app/registration.html", context)


def user_logout(request):
    logout(request)
    return redirect("home")


# http://127.0.0.0:8000/accounts/login/
# http://127.0.0.0:8000/login/


@login_required(login_url="login")
def add_post(request):
    if request.method == "POST":
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect("post_detail", form.pk)
    else:
        form = PostForm()

    context = {
        "form": form
    }
    return render(request, "blog_app/post_form.html", context)


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    success_url = "/"
    form_class = PostForm
    login_url = "/login/"

    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_superuser or self.request.user == obj.author

    def handle_no_permission(self):
        return redirect(self.login_url)


class PostDeleteView(DeleteView):
    model = Post
    template_name = "blog_app/post_confirm_delete.html"
    success_url = "/"


def user_posts_view(request, username):
    user = User.objects.filter(username=username).first()
    posts = Post.objects.filter(author=user)
    total_views = sum([post.views for post in posts])
    total_comments = sum([post.comments.all().count() for post in posts])
    registered_time = datetime.now().date() - user.date_joined.date()
    context = {
        "user": user,
        "posts": posts,
        "username": username,
        "total_views": total_views,
        "total_posts": posts.count(),
        "total_comments": total_comments,
        "registered_time": registered_time
    }
    return render(request, "blog_app/user_posts.html", context)


def add_vote(request, obj_type, obj_id, action):

    # if action == "add_like":
    obj = None
    if obj_type == "post":
        obj = get_object_or_404(Post, pk=obj_id)
    elif obj_type == "comment":
        obj = get_object_or_404(Comment, pk=obj_id)

    try:
        obj.dislikes
    except Exception as e:
        print(e)
        if obj.__class__ is Post:
            DisLike.objects.create(post=obj)
        else:
            DisLike.objects.create(comment=obj)

    try:
        obj.likes
    except Exception as e:
        if obj.__class__ is Post:
            Like.objects.create(post=obj)
        else:
            Like.objects.create(comment=obj)



    # если пользователь уже поставил лайк
    if action == "add_like":
        if request.user in obj.likes.user.all():
            obj.likes.user.remove(request.user.pk)  # удаляем лайк пользователя
        else:
            obj.likes.user.add(request.user.pk)
            obj.dislikes.user.remove(request.user.pk)
    elif action == "add_dislike":
        if request.user in obj.dislikes.user.all():
            obj.dislikes.user.remove(request.user.pk)  # удаляем лайк пользователя
        else:
            obj.dislikes.user.add(request.user.pk)
            obj.likes.user.remove(request.user.pk)
    else:
        return redirect("home")
    return redirect("home")
# TODO: обрезать описание статьи ✔
# TODO: сделать изменение статьи ✔
# TODO: сделать удаление статьи ✔
# TODO: сделать добавление комментария ✔
# TODO: сделать поиск ✔
# TODO: сделать счетчик просмотров ✔
# TODO: сделать страницу профиля ✔


# По плану
# TODO: Сделать вывод правильного времени

# Предложения
# TODO: Сделать лайкл дизлайк
# TODO: Сделать лайкл дизлайк для комментария
# TODO: Сделать репост статьи с добавлением свого описания
# TODO: Подписки на автора
# TODO: вывод статей по хэштегам


# TODO: Залить на хостинг
