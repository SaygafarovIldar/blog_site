from django.urls import path

from . import views


urlpatterns = [
    path("", views.HomeListView.as_view(), name="home"),  # http://127.0.0.1:8000/
    # path("", views.home_page, name="home"),  # http://127.0.0.1:8000/
    path("contacts/", views.contact_page, name="contacts"),  # http://127.0.0.1:8000/contacts/
    path("categories/<int:category_id>/", views.category_posts, name="category_posts"),  # http://127.0.0.1:8000/categories/1
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),  # http://127.0.0.1:8000/posts/1
    path("login/", views.login_view, name="login"),
    path("registration/", views.registration_view, name="registration"),
    path("logout/", views.user_logout, name="logout"),

    path("add_post/", views.add_post, name="add_post"),
    path("update_post/<int:pk>/", views.PostUpdateView.as_view(), name="update"),
    path("delete_post/<int:pk>/", views.PostDeleteView.as_view(), name="delete"),

    path("search/", views.SearchResults.as_view(), name="search"),
    path("profiles/<str:username>/", views.user_posts_view, name="user_posts"),

    path("<str:obj_type>/<int:obj_id>/<str:action>/", views.add_vote, name="add_vote"),
]

# http://127.0.0.1:8000/post/1/add_like
# http://127.0.0.1:8000/comment/1/add_like
