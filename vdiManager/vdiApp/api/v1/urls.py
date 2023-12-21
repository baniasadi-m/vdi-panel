from django.urls import path
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

app_name = "api-v1"

schema_view = get_schema_view(
   openapi.Info(
      title="VDI API",
      default_version='v1',
      description="VDI Api Document",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns =[
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('desktops', api_vdesktops, name='vdesktops'),
    path('desktops/<id>', api_vdesktops, name='vdesktops'),
    path('profiles', api_profiles, name='profiles'),
    path('profiles/<id>', api_profiles, name='profiless'),
    path('servers', api_servers, name='servers'),
    path('servers/<id>', api_servers, name='servers'),
    path('servers/<id>/check', server_check, name='servers'),
    path('search/<q>', search, name='search'),
]
