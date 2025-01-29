from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RatingListCreateView


app_name='Rating'


urlpatterns = [
    path('create/', RatingListCreateView.as_view(), name='rating-list-create'),
]
