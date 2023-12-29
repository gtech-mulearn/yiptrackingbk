from django.urls import path, include
from .views import UserRegisterAPI, UserAuthenticationAPI, GetAccessToken

urlpatterns = [
    path('user-authentication/', UserAuthenticationAPI.as_view()),
    path('refresh-token/', GetAccessToken.as_view()),
    path('register/', UserRegisterAPI.as_view()),
]
