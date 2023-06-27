from django.urls import path, include
from .views import *

app_name = "api-v1"

urlpatterns =[
    path('status', api_vdesktops, name='vdesktops')

]
