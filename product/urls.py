from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, PricingPredictionViewSet, PricingAdjustmentViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('orders', OrderViewSet)
router.register('pricing-predictions', PricingPredictionViewSet)
router.register('pricing-adjustments', PricingAdjustmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
