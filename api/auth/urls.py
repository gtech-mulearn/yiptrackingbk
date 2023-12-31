from django.urls import path, include
from .views import UserRegisterAPI, UserAuthenticationAPI, GetAccessToken, UserListAPI

urlpatterns = [
    path('user-authentication/', UserAuthenticationAPI.as_view()),
    path('refresh-token/', GetAccessToken.as_view()),
    path('register/', UserRegisterAPI.as_view()),
    path('user-list/', UserListAPI.as_view()),
    path('profile/', UserRegisterAPI.as_view()),
    path('profile/update/', UserRegisterAPI.as_view()),
]
