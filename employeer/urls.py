from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
path('api/employeer_register/', views.register_company_user, name='employeer_registration'),
path('api/employeer_login/', views.login_company_user, name='employeer_login'),
path('api/job-postings/', views.JobPostingCreateView.as_view(), name='job_postings'),
path('api/job-list-view/', views.JobPostingListView.as_view(), name='job-postings-list'),
path('api/job-list-view/<int:pk>/', views.JobPostingDetailView.as_view(), name='job-posting-detail'),
path('api/all-jobs/', views.AllJobsListView.as_view(), name='all-jobs'),
path('job-postings/<int:pk>/update/', JobPostingUpdateView.as_view(), name='job-update'),
]