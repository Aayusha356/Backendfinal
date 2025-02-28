from rest_framework import serializers
from rest_framework.fields import CharField
from django.conf import settings
from .models import Product, Category, Order, PricingPrediction, PricingAdjustment

User = settings.AUTH_USER_MODEL  # ✅ Get the CustomUser model dynamically

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    image_url = CharField(source='image.url', read_only=True)
    # Override the category field to return its name instead of its id
    category = CategorySerializer(read_only=True)  # Use CategorySerializer to serialize the full category

    def get_price_ratio(self, obj):
        if obj.cost_price and obj.current_price:
            return obj.current_price / obj.cost_price
        return None
    price_ratio = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'cost_price', 'current_price', 
            'category', 'image_url', 'size', 'price_ratio', 'sub_category', 
            'is_bestseller', 'created_at', 'updated_at', 'price_ratio', 
            'profit_margin', 'customer_rating'
        ]
    def get_price_ratio(self, obj):
        """ Calculate the price ratio as current_price / cost_price, ensuring it isn't zero """
        if obj.cost_price and obj.cost_price != 0:
            return obj.current_price / obj.cost_price
        return 0

    
class OrderSerializer(serializers.ModelSerializer):
    items = serializers.JSONField()  # ✅ Items stored as JSON
    user = serializers.CharField(source='user.username', read_only=True)  # ✅ Replace customer with user

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_price', 'items']


class PricingPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingPrediction
        fields = '__all__'


class PricingAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingAdjustment
        fields = '__all__'
