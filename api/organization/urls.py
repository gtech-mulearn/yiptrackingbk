from django.urls import path
from .views import OrganizationAPI, AssignOrganizationAPI, OrgVisitedAPI
urlpatterns = [
    path('', OrganizationAPI.as_view()),
    path('create/', OrganizationAPI.as_view()),
    path('assign/',AssignOrganizationAPI.as_view()),
    path('update-status/',OrgVisitedAPI.as_view()),
]
