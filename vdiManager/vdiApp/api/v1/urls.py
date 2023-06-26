from django.urls import path, include
from .views import *

app_name = "api-v1"

urlpatterns =[
    path('status', api_get_status, name='api-status')

]
