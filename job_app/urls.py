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
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
