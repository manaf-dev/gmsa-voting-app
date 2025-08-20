from django.urls import path
from .views import (
    UserViewset,
    reset_user_password,
    send_voting_reminders,
)
from .views import CookieTokenObtainPairView, CookieTokenRefreshView, JWTLogoutView
from .exhibition import (
    ExhibitionLookupView,
    ExhibitionRegisterView,
    ExhibitionPendingListView,
    ExhibitionVerifyView,
    ExhibitionPromoteVerifiedView,
    ExhibitionVerifyPromoteView,
    ExhibitionEntriesListView,  # new
    ExhibitionBulkVerifyView,   # new bulk verify
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
        "users/<str:user_id>/update/",
        UserViewset.as_view({"put": "update_user"}),
        name="update-user",
    ),
    path(
        "user/<uuid:user_id>/remove/",
        UserViewset.as_view({"post": "remove_user"}),
        name="remove-user",
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
    # JWT endpoints
    path("jwt/login/", CookieTokenObtainPairView.as_view(), name="jwt-login"),
    path("jwt/refresh/", CookieTokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/logout/", JWTLogoutView.as_view(), name="jwt-logout"),
    # Exhibition (public register check)
    path("exhibition/lookup/", ExhibitionLookupView.as_view(), name="exhibition-lookup"),
    path("exhibition/register/", ExhibitionRegisterView.as_view(), name="exhibition-register"),
    path("exhibition/pending/", ExhibitionPendingListView.as_view(), name="exhibition-pending"),
    path("exhibition/verify/<uuid:user_id>/", ExhibitionVerifyView.as_view(), name="exhibition-verify"),
    path("exhibition/promote/", ExhibitionPromoteVerifiedView.as_view(), name="exhibition-promote"),
    path("exhibition/verify-promote/<uuid:entry_id>/", ExhibitionVerifyPromoteView.as_view(), name="exhibition-verify-promote"),
    path("exhibition/entries/", ExhibitionEntriesListView.as_view(), name="exhibition-entries"),
    path("exhibition/bulk-verify/", ExhibitionBulkVerifyView.as_view(), name="exhibition-bulk-verify"),
]
