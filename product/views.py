from rest_framework.viewsets import ModelViewSet
from .models import Product, Category, Order, PricingAdjustment, PricingPrediction
import pandas as pd
import joblib
from ratings.models import Rating
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.preprocessing import StandardScaler
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import (
    ProductSerializer, CategorySerializer, 
    OrderSerializer, PricingPredictionSerializer, PricingAdjustmentSerializer
)
from ratings.serializers import RatingSerializer
from decimal import Decimal
from django.conf import settings

User = settings.AUTH_USER_MODEL  # Get the CustomUser model dynamically

# Load trained model & scaler
MODEL_PATH = r"C:/Users/Lenovo/Desktop/Backend3/finalbackend/regression_model/models/ridge_model.pkl"
SCALER_PATH = r"C:/Users/Lenovo/Desktop/Backend3/finalbackend/regression_model/models/ridge_scaler.pkl"

ridge_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

FEATURES = ['cost_price', 'current_price', 'customer_rating', 'discount', 'sales_volume', 'profit_margin', 'price_ratio']

@api_view(['GET'])
def predict_price_adjustment(request, product_id):
    try:
        # Fetch product by ID and load necessary fields (including computed price_ratio)
        product = get_object_or_404(Product.objects.only(*FEATURES), id=product_id)
        product_data = ProductSerializer(product).data

        # Fetch the rating from the rating app
        rating = Rating.objects.filter(product=product).aggregate(average_rating=Avg('rating'))['average_rating'] or 0
        product_data['customer_rating'] = rating

        # Prepare input data for the model
        input_data = pd.DataFrame([{
            feature: product_data.get(feature, 0)  # Default to 0 if the feature is missing
            for feature in FEATURES
        }])

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

# Views
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data) 
        # Fetch the logged-in user instead of Customer
        user = request.user

        # Get the items and total price from the request data
        items = request.data.get('items', [])
        if not items:
            return Response({"detail": "Items are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price and handle type conversions for each item
        total_price_value = 0
        item_data = []

        for item in items:
            try:
                # Convert price and quantity to correct types
                product = Product.objects.get(id=int(item["id"]))  # Fetch product by ID
                quantity = int(item["quantity"])  # Ensure quantity is an integer
                size = item["size"]
                price = float(item["price"])  # Convert price to float
                total_price_value += price * quantity  # Calculating total price

                # Add the item details
                item_data.append({
                    "product_id": product.id,
                    "quantity": quantity,
                    "size": size,
                    "price": price,
                    "name": product.name,
                    "image": item.get("image", ""),  # Optional image field
                })
            except ValueError:
                return Response({"detail": "Invalid data format for price or quantity."}, status=status.HTTP_400_BAD_REQUEST)
            except Product.DoesNotExist:
                return Response({"detail": f"Product with ID {item['id']} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order with the logged-in user instead of Customer
        order = Order.objects.create(
            user=user,
            total_price=total_price_value,
            items=item_data
        )

        # Serialize the created order and return the response
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PricingPredictionViewSet(ModelViewSet):
    queryset = PricingPrediction.objects.all()
    serializer_class = PricingPredictionSerializer

class PricingAdjustmentViewSet(ModelViewSet):
    queryset = PricingAdjustment.objects.all()
    serializer_class = PricingAdjustmentSerializer
