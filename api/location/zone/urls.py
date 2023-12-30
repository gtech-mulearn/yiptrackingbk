from django.urls import path
from .views import ZoneAPI
urlpatterns = [
    path('', ZoneAPI.as_view()),
    path('create/', ZoneAPI.as_view()),
]
