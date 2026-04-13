from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GetUserView, UserViewSet, ProductViewSet, CartItemViewSet, OrderViewSet


# Initialize the router
router = DefaultRouter()

# Register ViewSets
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')

# The router.urls property provides the full list of generated URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('me/', GetUserView.as_view(), name='get-user'),
]