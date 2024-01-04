from django.urls import path
from .views import DistrictAPI, DistrictSummaryAPI

urlpatterns = [
    path('', DistrictAPI.as_view()),
    path('create/', DistrictAPI.as_view()),
    path('summary/', DistrictSummaryAPI.as_view()),
]
