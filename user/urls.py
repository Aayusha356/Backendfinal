from django.urls import path
from .views import RegisterView, LoginView
#from product.models import user

urlpatterns = [
    #path('user/', RegisterView.as_view(), name='user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]
