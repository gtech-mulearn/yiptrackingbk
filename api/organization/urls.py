from django.urls import path
from .views import *

urlpatterns = [
    path('', OrganizationAPI.as_view()),
    path('create/', OrganizationAPI.as_view()),
    path('assign/', AssignOrganizationAPI.as_view()),
    path('update-status/', OrgVisitedAPI.as_view()),
    path('list/', OrganizationListAPI.as_view()),
    # path('idea/csv/',ImportOrgCSVAPI.as_view()),
    # path('idea/total/',OrganizationIdeaCountAPI.as_view()),
    # path('idea/users/',UserIdeaViewCountAPI.as_view()),
]
