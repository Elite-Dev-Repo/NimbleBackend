from django.urls import path
from . import views

urlpatterns = [
    path("initiate/",  views.InitiatePaymentView.as_view(),  name="payment-initiate"),
    path("verify/",    views.VerifyPaymentView.as_view(),    name="payment-verify"),
    # path("webhook/",   views.WebhookView.as_view(),          name="payment-webhook"),
]