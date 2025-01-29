from django.db import models
from django.conf import settings

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField()  
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rating({self.rating}) by {self.user} for {self.product}"
