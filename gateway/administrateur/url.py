from django.urls import path
from rest_framework.views import APIView
from . import views
from .views import AdministrateurApi,AdministrateurDetailsAPI,UsersApi
from rest_framework.authtoken import views


urlpatterns = [
    path('admin/', AdministrateurApi.as_view()),
    path('admin/<int:id>', AdministrateurDetailsAPI.as_view()),
    path('users/', UsersApi.as_view()),
]