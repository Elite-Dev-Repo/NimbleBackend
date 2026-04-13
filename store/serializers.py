from rest_framework import serializers
from .models import Product, Order, CartItem
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'image', 'created_at', 'size', 'color', 'keywords']

class CartItemSerializer(serializers.ModelSerializer):
    # 1. Nest the product details for the GET response
    product = ProductSerializer(read_only=True)
    
    # 2. Allow the frontend to send just the product ID when POSTing/Adding to cart
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), 
        source='product', 
        write_only=True
    )

    class Meta:
        model = CartItem
        # 3. Include both fields here
        fields = ['id', 'user', 'product', 'product_id', 'quantity', 'created_at']
        read_only_fields = ['user']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'quantity', 'total_price', 'created_at']
        read_only_fields = ['total_price']