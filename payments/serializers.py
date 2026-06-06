from rest_framework import serializers
from .models import Payment



class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "email",
            "order",
            "reference",
            "status"
        ]

        read_only_fields = [
            "reference",
            "status"
        ]