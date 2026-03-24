from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login, name='login'),
    path('api/profile/', views.ProfileDetail.as_view(), name='profile-detail'),
    path("api/profile/upload-resume/", views.upload_resume, name="upload-resume"),
    path('api/saved-jobs/', views.SavedJobListCreateView.as_view(), name='saved-jobs-list-create'),
    path('api/saved-jobs-all/', views.SavedJobListView.as_view(), name='saved-jobs-list-all'),
    path('api/saved-jobs/<int:pk>/', views.SavedJobDeleteView.as_view(), name='saved-jobs-delete'),
    path('api/verify-otp/', views.verify_otp, name='verify-otp'),
    path('api/send_otp/', views.send_otp, name='send-otp'),
    path('api/my-applied-jobs/', views.MyAppliedJobsView.as_view(), name='my-applied-jobs'),
    path('api/reset-password/', views.reset_password, name='request-password-reset'),
    path('api/forgot-password/', views.forgot_password, name='forgot-password'),
    path('api/profile/upload-profile-image/', views.image_upload, name='upload-profile-image')
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)