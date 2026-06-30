from rest_framework import generics,status, viewsets, permissions, serializers
from rest_framework.decorators import api_view, parser_classes, permission_classes, action
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer,SavedJobSerializer,SavedJobListSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .models import Profile,SavedJob,EmailOTP,CustomUser
from rest_framework.exceptions import NotAuthenticated
from django.core.mail import send_mail
from utils.utils import generate_otp, send_email, password_reset_token
from django.utils import timezone
from datetime import timedelta
from employeer.models import Application
from employeer.serializers import AppliedJobSerializer
from rest_framework.views import APIView
from django.conf import settings
import hashlib
from django.db import transaction,IntegrityError
from django.utils.crypto import constant_time_compare
from django.db.models import F
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
# from django.template.loader import get_template
from django.template.loader import render_to_string
import pdfkit
from bs4 import BeautifulSoup
import os

class AppliedJobPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50

class SavedJobPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 50

User = get_user_model()
OTP_EXPIRY_MINUTES = 1
OTP_RESEND_COOLDOWN_SECONDS = 60
MAX_OTP_ATTEMPTS = 3

def hash_otp(otp: str) -> str:
    secret = settings.SECRET_KEY
    return hashlib.sha256((otp + secret).encode()).hexdigest()

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def register(request):
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email is required"}, status=400)
    otp_verified = EmailOTP.objects.filter(email=email, is_used=True).exists()
    if not otp_verified:
        return Response({"error": "Please verify OTP first"},status=status.HTTP_400_BAD_REQUEST)
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        if User.objects.filter(email=serializer.validated_data['email']).exists():
            return Response({'error': 'User with this email already exists'} , status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        user.is_active = True
        user.is_verified = True
        user.role = 'job_seeker'
        user.save()

        resume_file = request.FILES.get("resume")
        Profile.objects.create(
            user=user,
            full_name=user.full_name,
            email=user.email,
            phone=user.mobile_number,
            country_id=request.data.get("country_id"),
            resume=resume_file if resume_file else None,
            phone_code=user.mobile_code
        )
        EmailOTP.objects.filter(email=email).delete()
        return Response({
            'message': 'Registration successful. Please verify OTP.',
            'user_id': user.id,
            'email': user.email,
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    user_role = CustomUser.objects.get(email=request.data.get("email")).role
    if user_role == 'employer' or user_role == 'admin':
        return Response({"error": "User Not Found Please Registerd"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
            if user:
                # token, created = Token.objects.get_or_create(user=user)
                refresh = RefreshToken.for_user(user)
                print("token>>>>>Token",refresh)
                return Response({
                    'message': 'Login successful',
                    'user_id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user_role': user.role
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Profile Page view

class ProfileDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Profile.objects.get_or_create(user=self.request.user)[0]
    def perform_update(self, serializer):
        profile = serializer.save()

        user = self.request.user
        if user.full_name != profile.full_name:
            user.full_name = profile.full_name
            user.save()

# Resume Upload view
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def upload_resume(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found."}, status=404)

    if 'resume' not in request.FILES:
        return Response({"error": "No resume file found in the request."}, status=400)

    profile.resume = request.FILES['resume']
    profile.save()

    return Response({"resume_url": profile.resume.url}, status=200)


class SavedJobListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedJobListView(generics.ListAPIView):
    serializer_class = SavedJobListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SavedJobPagination

    def get_queryset(self):
        queryset = SavedJob.objects.filter(user=self.request.user)
        total_jobs = queryset.count()
        return queryset


class SavedJobDeleteView(generics.DestroyAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    if not email or not otp:
        return Response({"error": "Email and OTP required"}, status=400)

    otp_hash = hash_otp(otp)
    valid_time = timezone.now() - timedelta(minutes=OTP_EXPIRY_MINUTES)

    with transaction.atomic():
        otp_obj = EmailOTP.objects.select_for_update().filter(
            email=email,
            is_used=False,
            created_at__gte=valid_time
        ).order_by('-created_at').first()

        if not otp_obj:
            return Response({"error": "Invalid or expired OTP"}, status=400)

        # Attempt limit check
        if otp_obj.attempts >= MAX_OTP_ATTEMPTS:
            otp_obj.delete()
            return Response({"error": "Too many attempts. Request new OTP."}, status=400)

        # Constant time comparison
        if not constant_time_compare(otp_obj.otp_hash, otp_hash):
            otp_obj.attempts = F('attempts') + 1
            otp_obj.save(update_fields=["attempts"])
            return Response({"error": "Invalid OTP"}, status=400)

        # Mark used
        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])

    return Response({"message": "OTP verified successfully"}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    email = request.data.get("email")
    if User.objects.filter(email=email).exists():
        return Response({"error": "User with this email already Registered"}, status=400)
    if not email:
        return Response({"error": "Email is required"}, status=400)

    # Always return generic message (prevent enumeration)
    generic_response = {"message": "OTP has been sent Already, Try again after 1 minutes!"}

    # Rate limiting: cooldown check
    existing_otp = EmailOTP.objects.filter(
        email=email,
        is_used=False
    ).order_by('-created_at').first()

    if existing_otp:
        elapsed = (timezone.now() - existing_otp.created_at).total_seconds()
        remaining = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            return Response(
            {"error": f"Please wait {remaining} seconds before requesting a new OTP."},
            status=400
            )

    # Delete only unused OTPs
    EmailOTP.objects.filter(email=email, is_used=False).delete()

    # Generate OTP
    otp = generate_otp()
    otp_hash = hash_otp(otp)

    # Store hashed OTP
    EmailOTP.objects.create(
        email=email,
        otp_hash=otp_hash,
        attempts=0
    )

    # Send email (ideally async in real production)
    send_email(
        to_email=email,
        subject="Your OTP Verification Code",
        template_name="Register_user.html",
        context={"otp": otp}
    )
    actual_response = {"message":"OTP Sent Successfully"}
    return Response(actual_response, status=200)

class MyAppliedJobsView(generics.ListAPIView):
    serializer_class = AppliedJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AppliedJobPagination

    def get_queryset(self):
        queryset = Application.objects.filter(user=self.request.user)
        total_jobs = queryset.count()
        print(total_jobs)
        return queryset
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get("email")

    try:
        user = User.objects.get(email=email)
        if not user:
            return Response({"error": "User not found"}, status=404)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = password_reset_token.make_token(user)

        reset_link = f"http://jobseeker-backend-jy1y.onrender.com/reset-password/{uid}/{token}/"

        # 🔥 Send email using SendGrid
        send_email(
            to_email=email,
            subject="Reset Your Password",
            template_name="Forget_password.html",
            context={"reset_link": reset_link}
        )

        return Response({"message": "Reset link sent to email"})

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    password = request.data.get("password")

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=user_id)

        if password_reset_token.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response({"message": "Password reset successful"})
        else:
            return Response({"error": "Invalid or expired token"}, status=400)

    except Exception:
        return Response({"error": "Invalid request"}, status=400)

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def image_upload(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found."}, status=404)

    if 'profile_image' not in request.FILES:
        return Response({"error": "No profile image file found in the request."}, status=400)

    profile.profile_image = request.FILES['profile_image']
    profile.save()

    return Response({"profile_image_url": profile.profile_image.url, "message": "Image uploaded successfully."}, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    token = request.data.get("token")
    if not token:
        return Response({"error": "Token is required"}, status=400)
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        email = idinfo.get("email")
        full_name = idinfo.get("name")
        if not email:
            return Response({"error": "Email not found"}, status=400)
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "full_name": full_name,
                "is_verified": True,
                "is_active": True,
                "role": "job_seeker",
            }
        )
        if created:
            Profile.objects.create(
                user=user,
                full_name=full_name,
                email=email,
            )
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
    except Exception as e:
        print("ERROR:", str(e))
        return Response({"error": str(e)}, status=400)
    

class DownloadResumeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, profile_id):
        return self.generate_pdf(request, profile_id)

    def post(self, request, profile_id):
        return self.generate_pdf(request, profile_id)

    def generate_pdf(self, request, profile_id):
        try:
           
            profile = Profile.objects.prefetch_related(
                "skills",
                "experiences",
                "educations",
                "certifications"
            ).select_related(
                "country",
                "state",
                "city"
            ).get(id=profile_id)
            
            serializer = ProfileSerializer(profile)
            data = serializer.data

            # Full image URL
            if data.get("profile_image"):
                data["profile_image"] = request.build_absolute_uri(
                    data["profile_image"]
                )
            
            html_string = render_to_string(
                "resume_template.html",
                {"profile": data}
            )

            summary = data.get("professional_summary", "")
            if summary:
                soup = BeautifulSoup(summary, "html.parser")

                for a in soup.find_all("a"):
                    a.decompose()

                data["professional_summary"] = str(soup)
            
            path_wkhtmltopdf = os.path.join(
                settings.BASE_DIR,
                "job_app",
                "wkhtmltopdf.exe"
            )

            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

            options = {
                "page-size": "A4",
                "encoding": "UTF-8",
                "margin-top": "0",
                "margin-right": "0",
                "margin-bottom": "0",
                "margin-left": "0",
                "enable-local-file-access": ""
            }
            
            pdf = pdfkit.from_string(
                html_string,
                False,
                configuration=config,
                options=options
            )
            
            response = HttpResponse(
                pdf,
                content_type="application/pdf"
            )

            response["Content-Disposition"] = (
                f'attachment; filename="resume_{profile_id}.pdf"'
            )

            return response

        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},
                status=404
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )
        