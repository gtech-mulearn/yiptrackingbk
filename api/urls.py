from django.urls import path, include
from rest_framework import routers

urlpatterns = [
    path('auth/', include('api.auth.urls')),
]
