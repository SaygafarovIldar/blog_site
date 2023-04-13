from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    title = models.CharField(verbose_name="Название категории", max_length=150)

    def get_absolute_url(self):
        return reverse("category_posts", kwargs={"category_id": self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Post(models.Model):
    title = models.CharField(verbose_name="Заголовок статьи", max_length=100)
    content = models.TextField(verbose_name="Описание статьи")  # TEXT
    image = models.ImageField(verbose_name="Фото статьи", upload_to="photos/", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now_add=True)
    views = models.IntegerField(verbose_name="Кол-во просмотров", default=0)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name="Категория")

    def get_comments_count(self):
        return self.comments.filter(post=self.pk).count()

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"post_id": self.pk})

    def __str__(self):
        return f"{self.title}: {self.author}"

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"


class Comment(models.Model):  # author post created_at content
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", blank=True, null=True, default=None)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f"{self.author}: {self.post}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class PostCountViews(models.Model):
    session_id = models.CharField(max_length=150, db_index=True)
    post = models.ForeignKey(Post, blank=True, null=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.session_id


class Like(models.Model):
    user = models.ManyToManyField(User, related_name="likes")
    post = models.OneToOneField(Post, related_name="likes", on_delete=models.CASCADE, null=True, blank=True)
    comment = models.OneToOneField(Comment, related_name="likes", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.post)


class DisLike(models.Model):
    user = models.ManyToManyField(User, related_name="dislikes")
    post = models.OneToOneField(Post, related_name="dislikes", on_delete=models.CASCADE, null=True, blank=True)
    comment = models.OneToOneField(Comment, related_name="dislikes", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.post)

