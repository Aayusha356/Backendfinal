from django.urls import path, include

from rest_framework.routers import DefaultRouter
from product.views import update_product_price
from .views import ProductViewSet, CategoryViewSet, CustomerViewSet, OrderViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('customers', CustomerViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('update-price/<int:product_id>/', update_product_price, name='update-price'),
]
