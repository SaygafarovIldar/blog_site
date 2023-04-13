from django.contrib import admin
from .models import Category, Post, Comment, PostCountViews

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "created_at", "updated_at", "views", "author", "category")
    list_display_links = ("pk", "title")
    list_editable = ("author", "category")
    list_filter = ("author", "category")


admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(PostCountViews)