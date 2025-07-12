from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/update/", views.update_profile_view, name="update_profile"),
    path("members/", views.MemberListView.as_view(), name="member_list"),
    path("academic-years/", views.academic_years_view, name="academic_years"),
    path("payment-status/", views.payment_status_view, name="payment_status"),
]
