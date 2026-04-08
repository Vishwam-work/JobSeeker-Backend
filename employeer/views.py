import profile

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .serializers import CompanyUserSerializer, CompanyLoginSerializer, JobPostingSerializer,AnswerSerializer, ApplicationSubmitSerializer, ApplicationListItemSerializer,CompanyListSerializer, CompanyDetailSerializer, JobPostingSerializer,ApplicationUpdateSerializer,InterviewScheduleSerializer,CompanyUserUpdateSerializer
from .models import CompanyUser, JobPosting,Answer, Application, JobClickEvent
from job_app.models import CustomUser
from master.models import Country, State, City
from rest_framework import generics,status, viewsets, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from django.db.models import F
from utils.utils import generate_otp, send_email
from job_app.models import EmailOTP, Profile
from django.utils import timezone
from datetime import timedelta
from job_app.serializers import ProfileSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import hashlib
from django.conf import settings
from django.db import transaction,IntegrityError
from django.utils.crypto import constant_time_compare

User = get_user_model()

OTP_EXPIRY_MINUTES = 1
OTP_RESEND_COOLDOWN_SECONDS = 60
MAX_OTP_ATTEMPTS = 3


def hash_otp(otp: str) -> str:
    secret = settings.SECRET_KEY
    return hashlib.sha256((otp + secret).encode()).hexdigest()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_company_user(request):
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email is required"}, status=400)
    otp_verified = EmailOTP.objects.filter(email=email, is_used=True).exists()
    if not otp_verified:
        return Response({"error": "Please verify OTP first"},status=status.HTTP_400_BAD_REQUEST)

    serializer = CompanyUserSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        company_user = serializer.save()
        company_user.is_verified = True
        company_user.is_active = True
        company_user.user.role = 'employer'
        company_user.user.save()
        company_user.save()
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
    user_role = CustomUser.objects.get(email=request.data.get("email")).role
    if user_role == 'job_seeker':
        return Response({"error": "User Not Found Please Register"}, status=status.HTTP_400_BAD_REQUEST)
    
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
    pagination_class = PageNumberPagination
    queryset = JobPosting.objects.filter(status='active').order_by('-created_at')

    def get_queryset(self):
        self.pagination_class.page_size = 5
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
    
class AnswerCreateView(generics.CreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            user = self.request.user
        except Exception:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(user=user)

# class ApplicationSubmitView(generics.CreateAPIView):
#     serializer_class = ApplicationSubmitSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         application = serializer.save()
#         job_id = serializer.validated_data['job_id']
#         JobPosting.objects.filter(id=job_id).update(applicants=F("applicants") + 1)
#         return Response(serializer.to_representation(application), status=status.HTTP_201_CREATED)
class ApplicationSubmitView(generics.CreateAPIView):
    serializer_class = ApplicationSubmitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        application = serializer.save()
        job = serializer.validated_data['job']

        # update applicant count safely
        JobPosting.objects.filter(id=job.id).update(applicants=F("applicants") + 1)

        return Response(
            serializer.to_representation(application),
            status=status.HTTP_201_CREATED
        )

class EmployerApplicationsListView(generics.ListAPIView):
    serializer_class = ApplicationListItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        # List applications for jobs belonging to the current employer
        try:
            company_user = CompanyUser.objects.get(user=self.request.user)
        except CompanyUser.DoesNotExist:
            return Application.objects.none()
        jobs = JobPosting.objects.filter(company_user=company_user)
        return Application.objects.filter(job__in=jobs).order_by('-applied_at')

# View to get the list of candidates for a specific job
class CandidateListView(generics.ListAPIView):
    serializer_class = ApplicationListItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        return Application.objects.filter(job_id=job_id).order_by('-applied_at')

@api_view(['GET'])
@permission_classes([AllowAny])
def company_list(request):
    """List all companies"""
    companies = CompanyUser.objects.select_related('country', 'state', 'city')
    serializer = CompanyListSerializer(companies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def company_detail(request, pk):
    """Get company details with job postings"""
    try:
        company = CompanyUser.objects.prefetch_related('job_postings').get(user_id=pk)
    except CompanyUser.DoesNotExist:
        return Response({'error': 'Company not found'}, status=404)
    serializer = CompanyDetailSerializer(company)
    return Response(serializer.data)

@api_view(['GET'])
def company_jobs(request, pk):
    """Get jobs for a specific company"""
    try:
        company = CompanyUser.objects.get(pk=pk)
    except CompanyUser.DoesNotExist:
        return Response({'error': 'Company not found'}, status=404)
    jobs = company.job_postings.filter(status='active')
    serializer = JobPostingSerializer(jobs, many=True)
    return Response(serializer.data)

class ApplicationUpdateView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        company_user = CompanyUser.objects.get(user=self.request.user)
        return Application.objects.filter(job__company_user=company_user)
    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.application_status == "rejected":
            user_email = instance.user.email

            send_email(
                to_email=user_email,
                subject="Application Rejected",
                template_name="Job_status.html",
                context={
                    "user": instance.user,
                    "job_title": instance.job.title,
                    "company_name": instance.job.company_user.company_name,
                    "application_status": instance.application_status
                }
            )
        elif instance.application_status == "shortlisted":
            user_email = instance.user.email

            send_email(
                to_email=user_email,
                subject="Application Shortlisted",
                template_name="Job_status.html",
                context={
                    "user": instance.user,
                    "job_title": instance.job.title,
                    "company_name": instance.job.company_user.company_name,
                    "job_description": instance.job.description,
                    "application_status": instance.application_status
                }
            )
# Get all the applications
class AllApplicationsListView(generics.ListAPIView):
    serializer_class = ApplicationListItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Application.objects.all().order_by('-applied_at')

class ScheduleInterviewView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = InterviewScheduleSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        instance = serializer.save(application_status="Interview Scheduled")
        email = instance.user.email
        send_email(
                to_email=email,
                subject="Interview Scheduled",
                template_name="Interview_schedule.html",
                context={
                    "user": instance.user,
                    "job": instance.job.title,
                    "date": instance.interview_date,
                    "time": instance.interview_time,
                    "mode": instance.interview_mode,
                    "link": instance.meet_link,
                    "notes": instance.notes,
                    "status": instance.application_status  #choices must be fromm the application model.
                }
        )

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

        if otp_obj.attempts >= MAX_OTP_ATTEMPTS:
            otp_obj.delete()
            return Response({"error": "Too many attempts. Request new OTP."}, status=400)

        if not constant_time_compare(otp_obj.otp_hash, otp_hash):
            otp_obj.attempts = F('attempts') + 1
            otp_obj.save(update_fields=["attempts"])
            return Response({"error": "Invalid OTP"}, status=400)

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

    generic_response = {"message": "If eligible, OTP has been sent"}

    existing_otp = EmailOTP.objects.filter(
        email=email,
        is_used=False
    ).order_by('-created_at').first()

    if existing_otp:
        elapsed = (timezone.now() - existing_otp.created_at).total_seconds()
        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            return Response(generic_response, status=200)

    EmailOTP.objects.filter(email=email, is_used=False).delete()

    otp = generate_otp()
    otp_hash = hash_otp(otp)

    EmailOTP.objects.create(
        email=email,
        otp_hash=otp_hash,
        attempts=0
    )

    # Send email (ideally async in real production)
    email_sent = send_email(
        to_email=email,
        subject="Your OTP Verification Code",
        template_name="Register_employer.html",
        context={"otp": otp}
    )
    if not email_sent:
        return Response(
            {"error": "Failed to send OTP email"},
            status=500
        )

    return Response({"message": "OTP sent successfully"}, status=200)

@api_view(["POST"])
@permission_classes([AllowAny])
def increment_job_click(request, job_id):
    request_id = request.data.get("request_id")

    if not request_id:
        return Response( {"error": "request_id is required"}, status=400)

    try:
        with transaction.atomic():
            JobClickEvent.objects.create(job_id=job_id,request_id=request_id)
            JobPosting.objects.filter(id=job_id).update(apply_clicks=F("apply_clicks") + 1)

    except IntegrityError:
         pass

    return Response(status=204)
    # return Response({
    #                   "job_clicks": JobPosting.apply_clicks,
    #                   "job_id" : JobPosting.id,
    #                   "request_id":request_id,
    #                 },status=200)
# All the Candidate Profile Views
class ProfileListAPIView(APIView):
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

class CompanyUserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        try:
            company = CompanyUser.objects.get(user_id=pk)
        except CompanyUser.DoesNotExist:
            return Response({'error': 'Company not found'}, status=404)

        serializer = CompanyUserSerializer(company)
        return Response(serializer.data)
class CompanyUserUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, pk):
        try:
            company = CompanyUser.objects.get(user__id=pk)
        except CompanyUser.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)

        serializer = CompanyUserUpdateSerializer(
            company,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Updated successfully"})

        return Response(serializer.errors, status=400)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def logo_upload(request):
    try:
        company = CompanyUser.objects.get(user=request.user)
    except CompanyUser.DoesNotExist:
        return Response({"error": "Company not found."}, status=404)

    if 'company_logo' not in request.FILES:
        return Response({"error": "No company logo file found in the request."}, status=400)

    company.company_logo = request.FILES['company_logo']
    company.save()

    return Response({"company_logo_url": company.company_logo.url, "message": "Logo uploaded successfully."}, status=200)