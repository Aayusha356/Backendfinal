from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from product.views import predict_price_adjustment, predict_price_adjustment_bulk

urlpatterns = [
    path('', include('product.urls')),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('ratings/',include('ratings.urls')),
    path('cart/', include('cart.urls')),
    path('predict/<int:product_id>/', predict_price_adjustment, name='predict_price'),
    path('predictbulk/', predict_price_adjustment_bulk, name='predict_price_adjustment_bulk'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)