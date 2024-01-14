from django.urls import path, include
import debug_toolbar

urlpatterns = [
    path('auth/', include('api.auth.urls')),
    path('location/', include('api.location.urls')),
    path('organization/', include('api.organization.urls')),
    path('ideaview/', include('api.ideaview.urls')),
    path("__debug__/", include(debug_toolbar.urls)),
]
