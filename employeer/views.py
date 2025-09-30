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

# Add the view for the view details
class JobPostingDetailView(generics.RetrieveAPIView):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_user = CompanyUser.objects.get(user=self.request.user)
        return JobPosting.objects.filter(company_user=company_user)

class JobPostingListView(generics.ListAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company_user = CompanyUser.objects.get(user=self.request.user)
        return JobPosting.objects.filter(company_user=company_user).order_by('-created_at')

class AllJobsListView(generics.ListAPIView):
    """
    View to fetch all jobs from the database
    This view is publicly accessible and returns all active job postings
    """
    serializer_class = JobPostingSerializer
    permission_classes = [AllowAny]
    queryset = JobPosting.objects.filter(status='active').order_by('-created_at')

    def get_queryset(self):

        queryset = JobPosting.objects.filter(status='active').order_by('-created_at')
        job_type = self.request.query_params.get('job_type', None)
        work_mode = self.request.query_params.get('work_mode', None)
        location = self.request.query_params.get('location', None)
        company = self.request.query_params.get('company', None)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        if work_mode:
            queryset = queryset.filter(work_mode=work_mode)
        if location:
            queryset = queryset.filter(location__name__icontains=location)
        if company:
            queryset = queryset.filter(company__icontains=company)
        return queryset

class JobPostingUpdateView(generics.UpdateAPIView):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Ensure that only the company user's jobs can be updated"""
        company_user = CompanyUser.objects.get(user=self.request.user)
        return JobPosting.objects.filter(company_user=company_user)

class JobPostingDeleteView(generics.DestroyAPIView):
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Limit the queryset so that a company user can only delete their own job postings."""
        company_user = CompanyUser.objects.get(user=self.request.user)
        return JobPosting.objects.filter(company_user=company_user)