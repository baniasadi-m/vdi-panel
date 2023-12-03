from django.urls import path, include
from .views import *
from django.views.generic import TemplateView

app_name = "api-v1"

urlpatterns =[
    path('desktops', api_vdesktops, name='vdesktops'),
    path('desktops/<id>', api_vdesktops, name='vdesktops'),
    path('profiles', api_profiles, name='profiles'),
    path('profiles/<id>', api_profiles, name='profiless'),
    path('servers', api_servers, name='servers'),
    path('servers/<id>', api_servers, name='servers'),
    path('servers/<id>/check', server_check, name='servers'),
    path('search/<q>', search, name='search'),
]
