from django.db import models
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from django.utils.timezone import now

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    SIZE_CHOICES = [('S', 'Small'),('M', 'Medium'),('L', 'Large'),]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.FloatField(default=0.0)
    sales_volume = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, null=True, blank=True)
    sub_category = models.CharField(max_length=50, blank=True, null=True)
    is_bestseller = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    price_ratio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profit_margin = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        """Ensure current_price is adjusted based on discount percentage."""
        if self.discount < 0 or self.discount > 100:
            raise ValueError("Discount must be between 0 and 100")

        if self.cost_price:
            # Apply discount to calculate current_price
            discounted_price = float(self.cost_price) * (1 - self.discount / 100)
            self.current_price = round(discounted_price, 2)

            # Ensure price ratio is updated
            if self.cost_price > 0.00:
                self.price_ratio = float(self.current_price) / float(self.cost_price)
    
    def __str__(self):
        return self.name
      

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
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

class PricingPrediction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    predicted_price_adjustment = models.DecimalField(max_digits=10, decimal_places=2)
    model_version = models.CharField(max_length=50)
    predicted_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"Prediction for {self.product.name} - {self.predicted_date}"

class PricingAdjustment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Adjustment for {self.product.name} at {self.created_at}"