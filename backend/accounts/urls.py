from django.urls import path
from .views import UserViewset

urlpatterns = [
    path("register/", UserViewset.as_view({"post": "register_user"}), name="register"),
    path(
        "register-bulk/",
        UserViewset.as_view({"post": "bulk_registration"}),
        name="bulk-register",
    ),
    path("login/", UserViewset.as_view({"post": "login"}), name="login"),
    path("logout/", UserViewset.as_view({"post": "logout"}), name="logout"),
    path("users/", UserViewset.as_view({"get": "list_users"}), name="list-users"),
    path(
        "users/<str:user_id>/retrieve/",
        UserViewset.as_view({"get": "retrieve_user"}),
        name="retrieve-user",
    ),
]
