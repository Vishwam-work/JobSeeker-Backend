from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .serializers import CompanyUserSerializer, CompanyLoginSerializer, JobPostingSerializer
from .models import CompanyUser, JobPosting
from master.models import Country, State, City
from rest_framework import generics,status, viewsets, permissions, serializers

User = get_user_model()
@api_view(['POST'])
@permission_classes([AllowAny])
def register_company_user(request):
    serializer = CompanyUserSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        company_user = serializer.save()
        refresh = RefreshToken.for_user(company_user.user)
        return Response({
            'message': 'Company user registered successfully',
            'user_id': company_user.user.id,
            'email': company_user.user.email,
            'company_name': company_user.company_name,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_company_user(request):
    serializer = CompanyLoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'user_id': user.id,
                    'email': user.email,
                    'company_name': user.companyuser.company_name,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobPostingCreateView(generics.CreateAPIView):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            company_user = CompanyUser.objects.get(user=self.request.user)
        except CompanyUser.DoesNotExist:
            return Response(
                {"detail": "Company profile not found for this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(
            company_user=company_user,
            company=company_user.company_name
        )

class JobPostingListView(generics.ListAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_user = CompanyUser.objects.get(user=self.request.user)
        return JobPosting.objects.filter(company_user=company_user).order_by('-created_at')