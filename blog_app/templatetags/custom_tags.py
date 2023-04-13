from blog_app.models import Category
from django import template

register = template.Library()


@register.simple_tag()
def get_categories():
    categories = Category.objects.all()
    return categories
