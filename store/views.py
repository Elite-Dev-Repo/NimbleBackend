from rest_framework import viewsets, permissions,generics
from .models import (
    Order,
    OrderItem,
    CartItem
    ,Product
)
from .serializers import ProductSerializer, OrderSerializer, UserSerializer, CartItemSerializer
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class GetUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        user = request.user

        cart_items = CartItem.objects.filter(
            user=user
        ).select_related("product")

        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty"},
                status=400
            )

        total_price = 0

        # Create order
        order = Order.objects.create(
            user=user
        )

        order_items = []

        for item in cart_items:

            total_price += (
                item.product.price * item.quantity
            )

            order_items.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price
                )
            )

        OrderItem.objects.bulk_create(order_items)

        order.total_price = total_price
        order.save()

        serializer = self.get_serializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )