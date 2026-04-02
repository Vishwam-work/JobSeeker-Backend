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
path('job-postings/<int:pk>/update/', views.JobPostingUpdateView.as_view(), name='job-update'),
path('job-postings/<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='job-delete'),
path('save-answers/', views.AnswerCreateView.as_view(), name='save-answers'),
path('api/applications/submit/', views.ApplicationSubmitView.as_view(), name='application-submit'),
path('api/employer/applications/', views.EmployerApplicationsListView.as_view(), name='employer-applications-list'),
path('api/companies/', views.company_list, name='company-list'),
path('api/companies/<int:pk>/', views.company_detail, name='company-detail'),
path('api/companies/<int:pk>/jobs/', views.company_jobs, name='company-jobs'),
path('api/employer/applications/<int:pk>/update/', views.ApplicationUpdateView.as_view(), name='application-update'),
path('api/employer/applications/all/', views.AllApplicationsListView.as_view(), name='application-all'),
path('api/employer/applications/job/<int:job_id>', views.CandidateListView.as_view(), name='candidate-sort'),
path("api/employer/applications/<int:pk>/schedule-interview/",views.ScheduleInterviewView.as_view(),name="schedule-interview"),
path('api/verify-otp/', views.verify_otp, name='verify-otp'),
path('api/send_otp/', views.send_otp, name='send-otp'),
path("api/<int:job_id>/click/", views.increment_job_click),
path('api/profile-all/', views.ProfileListAPIView.as_view(), name='profile-detail'),
path('api/company/<int:pk>/', views.CompanyUserDetail.as_view(), name='company-detail'),
path('api/company/<int:pk>/update/', views.CompanyUpdateView.as_view(), name='company-update'),
path('api/company/upload-company-logo/', views.logo_upload, name='upload-company-logo')

] 