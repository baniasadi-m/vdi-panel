from django.urls import path
from .views import *

app_name = 'vdiApp'
urlpatterns = [
    path('',dashboard , name='dashboard'),
]