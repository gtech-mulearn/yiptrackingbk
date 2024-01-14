from django.urls import path
from .views import *

urlpatterns = [
    path('total/', TotalIdeaCountAPI.as_view()),
    path('csv/', ImportOrgCSVAPI.as_view()),
    path('list/', IdeaCountListAPI.as_view()),
]
