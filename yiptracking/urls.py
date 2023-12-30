from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/v1/yiptracking', include('api.urls')),
]
