import os
import joblib
import pandas as pd

# Load AI Model
MODEL_PATH = os.path.join("utils", "ridge_model.pkl")
model = joblib.load(MODEL_PATH)

def predict_price(product_data):
    """ Predict the product price using the AI model. """
    predicted_price = model.predict(product_data)
    return predicted_price[0]

     