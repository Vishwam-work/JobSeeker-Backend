from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('api/countries/', views.CountryList.as_view(), name='country-list'),
    path('api/states/', views.StateList.as_view(), name='state-list'),
    path('api/cities/', views.CityList.as_view(), name='city-list'),
    path('api/companies/', views.CompanyList.as_view(), name='company-list'),
    path('api/jobs_category/', views.JobCategoryList.as_view(), name='job-category'),
    path('api/jobs_title/', views.JobTitleList.as_view(), name='job-list'),
    path('api/currencies/', views.CurrencyList.as_view(), name='currency-list'),
]
