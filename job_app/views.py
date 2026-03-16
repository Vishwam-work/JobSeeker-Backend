from rest_framework import generics,status, viewsets, permissions, serializers
from rest_framework.decorators import api_view, parser_classes, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer,SavedJobSerializer,SavedJobListSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .models import Profile,SavedJob,EmailOTP,CustomUser
from rest_framework.exceptions import NotAuthenticated
from django.core.mail import send_mail
from utils.utils import generate_otp, send_email
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
            resume=resume_file if resume_file else None
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
    if user_role == 'employer':
        return Response({"error": "Employer login is not allowed"}, status=status.HTTP_400_BAD_REQUEST)
    
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

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)


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

    if not email:
        return Response({"error": "Email is required"}, status=400)

    # Always return generic message (prevent enumeration)
    generic_response = {"message": "OTP has been sent Already, Try again after 5 minutes!"}

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

class MyAppliedJobsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        applications = Application.objects.filter(user=request.user)
        serializer = AppliedJobSerializer(applications, many=True)
        return Response(serializer.data)
