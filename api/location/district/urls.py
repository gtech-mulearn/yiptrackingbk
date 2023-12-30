from django.urls import path
from .views import DistrictAPI
urlpatterns = [
    path('', DistrictAPI.as_view()),
    path('create/', DistrictAPI.as_view()),
]
