from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from payments.client import paystack
from .models import Payment
from .serializers import PaymentSerializer
from store.models import Order


class InitiatePaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order = data.get("order")

        if order and order.user_id != request.user.id:
            return Response({"error": "Order not found"}, status=404)

        payment = Payment.objects.create(
            user=request.user,
            email=data["email"],
            amount=int(data["amount"] * 100),
            order=order,
        )

        res = paystack.post("/transaction/initialize", json={
            "email":        data["email"],
            "amount":       payment.amount,
            "reference":    str(payment.reference),
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
            "metadata": {
                "payment_id": payment.pk,
                "order_id": str(payment.order_id) if payment.order_id else None,
            },
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
    def get(self, request, reference=None):
        reference = reference or request.query_params.get("reference")
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

        tx_status = tx.get("status")
        payment_status = tx_status if tx_status in dict(Payment.STATUS_CHOICES) else payment.status
        order_status = None

        if tx_status == "success":
            payment.paid_at = timezone.now()
            order_status = Order.PaymentStatus.PAID
        elif tx_status in {"failed", "abandoned"}:
            payment.paid_at = None
            order_status = Order.PaymentStatus.FAILED

        payment.status = payment_status
        payment.channel = tx.get("channel") or ""
        payment.currency = tx.get("currency") or payment.currency

        with transaction.atomic():
            payment.save(update_fields=["status", "channel", "currency", "paid_at"])
            if payment.order_id and order_status:
                payment.order.payment_status = order_status
                payment.order.save(update_fields=["payment_status"])

        return Response({
            "status":    tx_status,
            "payment_status": payment.status,
            "order_payment_status": payment.order.payment_status if payment.order_id else None,
            "amount":    tx["amount"] / 100,
            "currency":  tx.get("currency"),
            "channel":   tx.get("channel"),
            "paid_at":   tx.get("paid_at"),
            "reference": tx["reference"],
        })
