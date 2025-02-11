from celery import shared_task
from .models import Product, PricingPrediction
from decimal import Decimal
import pandas as pd
import joblib
import os

# Load trained model & scaler
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "regression_model/models/ridge_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "regression_model/models/ridge_scaler.pkl")

ridge_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

FEATURES = ['cost_price', 'current_price', 'customer_rating', 'discount', 'sales_volume', 'profit_margin', 'price_ratio']

@shared_task
def predict_price_adjustment_bulk():
    try:
        products = Product.objects.only("id", "current_price", "cost_price").all()
        lambda_factor = Decimal('0.5')

        for product in products:
            current_price = Decimal(product.current_price or "0.00")
            cost_price = Decimal(product.cost_price or "0.00")

            # Prepare data for prediction
            input_data = pd.DataFrame([{feature: getattr(product, feature, 0) for feature in FEATURES}])
            input_scaled = scaler.transform(input_data)

            # Predict price adjustment
            predicted_adjustment = ridge_model.predict(input_scaled)[0]
            predicted_adjustment = Decimal(str(predicted_adjustment))

            # Compute new price
            target_price = cost_price + predicted_adjustment
            new_price = (Decimal(1) - lambda_factor) * current_price + lambda_factor * target_price

            # Update the product price
            Product.objects.filter(id=product.id).update(current_price=new_price)

            # Store prediction in the database
            PricingPrediction.objects.update_or_create(
                product=product,
                defaults={"predicted_price_adjustment": predicted_adjustment}
            )

        return f"Updated prices for {products.count()} products."

    except Exception as e:
        return str(e)

# ---- Celery Beat Configuration for Periodic Tasks ----
from celery.schedules import crontab
from celery import Celery

app = Celery('ecommerce')

# Use RabbitMQ as the broker
app.conf.broker_url = 'pyamqp://guest@localhost//'

# Schedule the task to run every minute
app.conf.beat_schedule = {
    'run-price-adjustment-every-hour': {
        'task': 'product.tasks.predict_price_adjustment_bulk',
        'schedule': crontab(minute='*'),  # Runs every minute
    },
}
