from django.urls import path
from . import views

urlpatterns = [
    path("initiate/", views.InitiatePaymentView.as_view(), name="initiate-payment"),
    path("webhook/", views.PaystackWebhookView.as_view(), name="paystack-webhook"),
    path("verify/<str:reference>/", views.verify_payment, name="verify-payment"),
    path("my-payments/", views.user_payments, name="user-payments"),
    path("stats/", views.payment_stats, name="payment-stats"),
]
