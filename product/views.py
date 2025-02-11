from rest_framework.viewsets import ModelViewSet
from .models import Product, Category, Customer, Order, OrderItem, PricingAdjustment, PricingPrediction
import pandas as pd
import joblib
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.preprocessing import StandardScaler
from .serializers import (
    ProductSerializer, CategorySerializer, CustomerSerializer, 
    OrderSerializer, OrderItemSerializer, PricingPredictionSerializer, PricingAdjustmentSerializer
)
from decimal import Decimal

# Load trained model & scaler
MODEL_PATH = r"C:\Users\sache\projects\minprjct\regression_model\models\ridge_model.pkl"
SCALER_PATH = r"C:\Users\sache\projects\minprjct\regression_model\models\ridge_scaler.pkl"

ridge_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

FEATURES = ['cost_price', 'current_price', 'customer_rating', 'discount', 'sales_volume', 'profit_margin', 'price_ratio']

@api_view(['GET'])
def predict_price_adjustment(request, product_id):
    try:
        # Fetch product by ID and load necessary fields (including computed price_ratio)
        product = get_object_or_404(Product.objects.only(*FEATURES), id=product_id)
        product_data = ProductSerializer(product).data

        # Prepare input data for the model
        input_data = pd.DataFrame([{
            feature: product_data.get(feature, 0)  # Default to 0 if the feature is missing
            for feature in FEATURES
        }])

        # Handle missing or invalid data gracefully if needed

        # Scale input data for model prediction
        input_scaled = scaler.transform(input_data)

        # Predict price adjustment
        predicted_adjustment = ridge_model.predict(input_scaled)[0]
        predicted_adjustment = Decimal(str(predicted_adjustment))  # Convert float to Decimal

        # Extract prices for later use
        current_price = Decimal(product.current_price or "0.00")
        cost_price = Decimal(product.cost_price or "0.00")

        # Define lambda (smoothing factor)
        lambda_factor = Decimal('0.5')

        # Calculate target price (cost_price + predicted adjustment)
        target_price = cost_price + predicted_adjustment

        # Calculate the new price using the weighted average formula
        new_price = (1 - lambda_factor) * current_price + lambda_factor * target_price

        # Update the product with the new calculated price
        Product.objects.filter(id=product.id).update(current_price=new_price)

        # Store the prediction in the database
        PricingPrediction.objects.update_or_create(
            product=product,
            defaults={"predicted_price_adjustment": predicted_adjustment}
        )

        # Return the response with updated price information
        return Response({
            "product_id": product.id,
            "new_current_price": new_price,
            "predicted_price_adjustment": predicted_adjustment
        })

    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def predict_price_adjustment_bulk(request):
    try:
        products = Product.objects.only(*FEATURES).all()  # Fetch the needed features for each product
        results = []

        # Define lambda (smoothing factor)
        lambda_factor = Decimal('0.5')

        for product in products:
            product_data = ProductSerializer(product).data

            # Prepare input data for the model
            input_data = pd.DataFrame([{
                feature: product_data.get(feature, 0)  # Default to 0 if the feature is missing
                for feature in FEATURES
            }])

            # Scale input data for model prediction
            input_scaled = scaler.transform(input_data)

            # Predict price adjustment
            predicted_adjustment = ridge_model.predict(input_scaled)[0]
            predicted_adjustment = Decimal(str(predicted_adjustment))

            # Extract prices for later use
            current_price = Decimal(product.current_price or "0.00")
            cost_price = Decimal(product.cost_price or "0.00")

            # Calculate target price (cost_price + predicted adjustment)
            target_price = cost_price + predicted_adjustment

            # Calculate the new price using the weighted formula
            new_price = (Decimal(1) - lambda_factor) * current_price + lambda_factor * target_price

            # Update the product with the new calculated price
            Product.objects.filter(id=product.id).update(current_price=new_price)

            # Store the prediction in the database
            PricingPrediction.objects.update_or_create(
                product=product,
                defaults={"predicted_price_adjustment": predicted_adjustment}
            )

            # Append the result for this product
            results.append({
                "product_id": product.id,
                "new_current_price": new_price,
                "predicted_price_adjustment": predicted_adjustment
            })

        # Return the response with the results for all products
        return Response(results)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

#views
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

class PricingPredictionViewSet(ModelViewSet):
    queryset = PricingPrediction.objects.all()
    serializer_class = PricingPredictionSerializer

class PricingAdjustmentViewSet(ModelViewSet):
    queryset = PricingAdjustment.objects.all()
    serializer_class = PricingAdjustmentSerializer