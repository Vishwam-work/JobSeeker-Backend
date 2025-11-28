from rest_framework import generics,status, viewsets, permissions, serializers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer,SavedJobSerializer,SavedJobListSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .models import Profile,SavedJob
from rest_framework.exceptions import NotAuthenticated
from django.core.mail import send_mail
from .utils import generate_otp

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        if User.objects.filter(email=serializer.validated_data['email']).exists():
            return Response({'error': 'User with this email already exists'} , status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        user.is_active = False  
        user.otp = generate_otp()
        user.save()

        send_mail(
            "Your OTP Verification Code",
            f"Your OTP is: {user.otp}",
            "akshitsahore282007@gmail.com",
            [user.email],
        )

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

    try:
        user = User.objects.get(email=email)

        if  user.otp == otp:
            user.is_active = True
            user.is_verified = True
            user.otp = None
            user.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "OTP verification successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.id,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

