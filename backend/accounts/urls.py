from django.urls import path
from .views import (
    UserViewset,
    reset_user_password,
    send_voting_reminders,
)

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
    path(
        "password/change/",
        UserViewset.as_view({"post": "change_password"}),
        name="change-password",
    ),
    # SMS and admin functions
    path(
        "admin/add-user/",
        UserViewset.as_view({"post": "admin_add_user"}),
        name="admin-add-user",
    ),
    path("admin/reset-password/", reset_user_password, name="reset-password"),
    path(
        "admin/send-voting-reminders/",
        send_voting_reminders,
        name="send-voting-reminders",
    ),
]
