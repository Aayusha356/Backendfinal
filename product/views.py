
from rest_framework.viewsets import ModelViewSet
from .models import Product, Category, Customer, Order, OrderItem
from django.http import JsonResponse
import pandas as pd
import joblib
from .serializers import (
    ProductSerializer, CategorySerializer, CustomerSerializer, 
    OrderSerializer, OrderItemSerializer
)
from utils.AI_script import predict_price


def update_product_price(request, product_id):
    try:
        product = Product.objects.get(id=product_id)

        # Prepare data for prediction
        product_data = pd.DataFrame({
            'rating': [product.customer_rating],
            'demand': [product.sales_volume],
            'discount': [product.discount],
            'price': [float(product.price)],  # Convert to float
        })

        # Predict price using AI model
        predicted_price = predict_price(product_data)

        # Update product price
        product.current_price = predicted_price
        product.save()

        return JsonResponse({"new_price": predicted_price})

    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

