from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
path('api/employeer_register/', views.register_company_user, name='employeer_registration'),
path('api/employeer_login/', views.login_company_user, name='employeer_login'),
]