from rest_framework import serializers
from .models import Rating

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        ##fields = ['id', 'user', 'product', 'rating', 'review', 'created_at']
        ##read_only_fields = ['id', 'created_at', 'user']
