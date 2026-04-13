from django.shortcuts import render

# Create your views here.
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from django.utils import timezone

from payments.client import paystack
from .models import Payment
from .serializers import PaymentSerializer

class InitiatePaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        payment = Payment.objects.create(
            user=request.user,
            email=data["email"],
            amount=data["amount"] * 100,
        )

        res = paystack.post("/transaction/initialize", json={
            "email":        data["email"],
            "amount":       payment.amount,
            "reference":    str(payment.reference),
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
            "metadata":     {"payment_id": payment.pk},
            "channels":     ["card", "bank", "ussd", "bank_transfer"],
        })

        body = res.json()
        if not body["status"]:
            payment.delete()
            return Response({"error": body["message"]}, status=502)

        return Response({
            "authorization_url": body["data"]["authorization_url"],
            "reference":         str(payment.reference),
        }, status=201)
    



class VerifyPaymentView(APIView):
    def get(self, request):
        reference = request.query_params.get("reference")
        if not reference:
            return Response({"error": "reference is required"}, status=400)

        try:
            payment = Payment.objects.get(reference=reference, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

        res = paystack.get(f"/transaction/verify/{reference}")
        body = res.json()

        if not body["status"]:
            return Response({"error": body["message"]}, status=502)

        tx = body["data"]

        # Update local record
        if tx["status"] == "success":
            payment.status  = "success"
            payment.channel = tx.get("channel", "")
            payment.paid_at = timezone.now()
            payment.save(update_fields=["status", "channel", "paid_at"])

        return Response({
            "status":    tx["status"],
            "amount":    tx["amount"] / 100,
            "currency":  tx["currency"],
            "channel":   tx.get("channel"),
            "paid_at":   tx.get("paid_at"),
            "reference": tx["reference"],
        })