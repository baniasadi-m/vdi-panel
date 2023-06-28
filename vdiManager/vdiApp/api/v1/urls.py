from django.urls import path, include
from .views import *

app_name = "api-v1"

urlpatterns =[
    path('desktops', api_vdesktops, name='vdesktops'),
    path('desktops/<id>', api_vdesktops, name='vdesktops'),
    # path('desktops', api_vdesktops, name='vdesktops'),

]
