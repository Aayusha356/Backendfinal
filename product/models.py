from django.db import models
from django.conf import settings
from django.utils import timezone

import pandas as pd
from rest_framework.response import Response



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Set default value
    discount = models.FloatField(default=0.0)  # Discount percentage
    sales_volume = models.IntegerField(default=0)  # Total units sold
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Profit percentage
    price_ratio = models.FloatField(blank=True, null=True) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, null=True, blank=True)
    sub_category = models.CharField(max_length=50, blank=True, null=True)
    is_bestseller = models.BooleanField(default=False)  # Bestseller flag
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    customer_rating = models.FloatField(default=0.0)
    sales_volume = models.IntegerField(default=0)
    discount = models.FloatField(default=0.0)
    price_ratio = models.FloatField(default=0.0)
    profit_margin = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        """Automatically calculate price ratio before saving."""
        if self.cost_price:
            self.price_ratio = float(self.current_price) / float(self.cost_price)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

