from rest_framework import generics,status, viewsets, permissions, serializers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer,SavedJobSerializer,SavedJobListSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .models import Profile,SavedJob,EmailOTP
from rest_framework.exceptions import NotAuthenticated
from django.core.mail import send_mail
from utils.utils import generate_otp, send_email
from django.utils import timezone
from datetime import timedelta
from employeer.models import Application
from employeer.serializers import AppliedJobSerializer
from rest_framework.views import APIView

User = get_user_model()
OTP_EXPIRY_MINUTES = 5

@api_view(['POST'])
@permission_classes([AllowAny])
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
        user.save()
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

    try:
        otp_obj = EmailOTP.objects.get(
            email=email,
            otp=otp,
            is_used=False
        )
    except EmailOTP.DoesNotExist:
        return Response({"error": "Invalid OTP"}, status=400)

    expiry_time = otp_obj.created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
    if timezone.now() > expiry_time:
        otp_obj.delete()
        return Response({"error": "OTP expired"}, status=400)

    otp_obj.is_used = True
    otp_obj.save(update_fields=["is_used"])

    return Response({"message": "OTP verified successfully"}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email is required"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "User already exists"}, status=400)

    EmailOTP.objects.filter(email=email).delete()

    otp = generate_otp()

    EmailOTP.objects.create(
        email=email,
        otp=otp,
    )

    email_sent = send_email(
        to_email=email,
        subject="Your OTP Verification Code",
        template_name="Register_user.html",
        context={"otp":otp},
    )
    if not email_sent:
        return Response(
            {"error": "Failed to send OTP email"},
            status=500
        )

    return Response({"message": "OTP sent successfully"}, status=200)

class MyAppliedJobsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        applications = Application.objects.filter(user=request.user)
        serializer = AppliedJobSerializer(applications, many=True)
        return Response(serializer.data)