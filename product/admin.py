from django.contrib import admin
from .models import Category, Product, Order

from django.conf import settings

User = settings.AUTH_USER_MODEL
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'cost_price', 'current_price', 'sales_volume')  # Add 'category' here
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price','items', 'created_at')  # Display user
    search_fields = ('user__username',)  # Allow searching by username


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order,OrderAdmin)


