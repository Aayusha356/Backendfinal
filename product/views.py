
from rest_framework.viewsets import ModelViewSet
from .models import Product, Category, Customer, Cart, CartItem, Order, OrderItem
from .serializers import (
    ProductSerializer, CategorySerializer, CustomerSerializer, 
    CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
)

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

