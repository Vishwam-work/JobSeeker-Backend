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
    # Education mojors paths
    path('api/categories/', views.MajorCategoryListView.as_view(), name='major_categories'),
    path('api/majors/', views.MajorListView.as_view(), name='major_list'),
    path('api/majors/<int:pk>/', views.MajorDetailView.as_view(), name='major_detail'),
    path('api/majors/category/<int:category_id>/', views.MajorsByCategoryView.as_view(), name='majors_by_category'),
    # Course search path
    path('api/courses/search/', views.search_courses, name='search-courses'),
    path('api/courses/create/', views.create_course, name='create-course'),
]
