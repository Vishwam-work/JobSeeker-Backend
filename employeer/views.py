import profile

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, filters
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .serializers import CompanyUserSerializer, CompanyLoginSerializer, JobPostingSerializer,AnswerSerializer, ApplicationSubmitSerializer, ApplicationListItemSerializer,CompanyListSerializer, CompanyDetailSerializer, JobPostingSerializer,ApplicationUpdateSerializer,InterviewScheduleSerializer,CompanyUserUpdateSerializer,ViewdprofileSerializer,SavedProfileSerializer
from .models import CompanyUser, JobPosting,Answer, Application, JobClickEvent,SaveProf,ViewdProfile
from job_app.models import CustomUser
from master.models import Country, State, City
from rest_framework import generics,status, viewsets, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from django.db.models import F,Q
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
from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework.pagination import PageNumberPagination

User = get_user_model()

class SavedProfPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 50

OTP_EXPIRY_MINUTES = 1
OTP_RESEND_COOLDOWN_SECONDS = 60
MAX_OTP_ATTEMPTS = 3


def hash_otp(otp: str) -> str:
    secret = settings.SECRET_KEY
    return hashlib.sha256((otp + secret).encode()).hexdigest()

class JobPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 50

class CandidatePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50

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
    if user_role == 'admin':
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
                    {'error': 'User with this email does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
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
            company_user=company_user
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
    pagination_class = JobPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'company', 'location']

    def get_queryset(self):
        company_user = CompanyUser.objects.get(user=self.request.user)
        queryset = JobPosting.objects.filter(company_user=company_user).order_by('-created_at')

        status = self.request.query_params.get('status')
        if status and status != 'all':
            queryset = queryset.filter(status__iexact=status)

        date_filter = self.request.query_params.get('date_filter')
        now = timezone.now()
        if date_filter == 'today':
            queryset = queryset.filter(created_at__date=now.date())
        elif date_filter == 'week':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
        elif date_filter == 'month':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=30))
        elif date_filter == 'year':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=365))
        print(queryset)
        return queryset
        # return JobPosting.objects.filter(company_user=company_user).order_by('-created_at')

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
        self.pagination_class.page_size = 3
        queryset = JobPosting.objects.filter(status='active').order_by('-created_at')
        job_type = self.request.query_params.getlist('job_type', None)
        work_mode = self.request.query_params.getlist('work_mode', None)
        location = self.request.query_params.get('location', None)
        company = self.request.query_params.getlist('company', None)
        search = self.request.query_params.get('search', None)
        experience = self.request.query_params.getlist('experience', None)
        salary_ranges = self.request.query_params.getlist('salary_range', None)
        if job_type:
            queryset = [
                job for job in queryset
                if any(jt in (job.job_type or []) for jt in job_type)
            ]
        if work_mode:
            print(work_mode)
            queryset = [
                job for job in queryset
                if any(wm in (job.work_mode or []) for wm in work_mode)
            ]
        if location:
            queryset = queryset.filter(location=location)
        if company:
            queryset = [
                comp for comp in queryset
                if any(wm in (comp.company or []) for wm in company)
            ]
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(company__icontains=search) |
                Q(location__icontains=search)
            )
        if salary_ranges:
            queryset = queryset.annotate(
                salary_int=Cast('salary', IntegerField()),
                salary_max_int=Cast('salary_max', IntegerField())
            )

            salary_query = Q()

            for sr in salary_ranges:
                if "+" in sr:
                    min_salary = int(sr.replace("+", "")) * 100000
                    salary_query |= Q(salary_int__gte=min_salary) | Q(salary_max_int__gte=min_salary)

                elif "-" in sr:
                    min_salary, max_salary = sr.split('-')
                    min_salary = int(min_salary) * 100000
                    max_salary = int(max_salary) * 100000

                    salary_query |= Q(salary_int__gte=min_salary) & Q(salary_int__lte=max_salary) | Q(salary_max_int__gte=min_salary) & Q(salary_max_int__lte=max_salary)

            queryset = queryset.filter(salary_query)
        if experience:
            queryset = queryset.filter(experience__in=experience)
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
    pagination_class = CandidatePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__full_name', 'job__title']
    def get_queryset(self):
        # List applications for jobs belonging to the current employer
        try:
            company_user = CompanyUser.objects.get(user=self.request.user)
        except CompanyUser.DoesNotExist:
            return Application.objects.none()

        jobs = JobPosting.objects.filter(company_user=company_user)

        queryset = Application.objects.filter(job__in=jobs).order_by('-applied_at')
        status = self.request.query_params.get('status')
        if status and status != "All":
            queryset = queryset.filter(application_status__iexact=status)

        gender = self.request.query_params.get('gender')
        if gender and gender != "All":
            queryset = queryset.filter(user__profile__gender=gender)

        job_title = self.request.query_params.get('job_title')
        if job_title and job_title != "All":
            queryset = queryset.filter(job__title__icontains=job_title)

        location = self.request.query_params.get('location')
        if location and location != "All":
            queryset = queryset.filter(user__profile__state__name__icontains=location)

        experience = self.request.query_params.get('experience')
        if experience and experience != "All":
            queryset = queryset.filter(user__profile__experience__icontains=experience)

        return queryset

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


class SavedProfileListCreateView(APIView):

    def post(self, request):
        profile_id = request.data.get("profile")

        profile = Profile.objects.get(id=profile_id)

        saved_profile = SaveProf.objects.create(
            user=CompanyUser.objects.get(user=request.user),
            profile=profile
        )

        return Response({
            "message": "Profile saved successfully"
        })


class ViewedProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        user = request.user
        profile_id = request.data.get("profile_ids")
        # check profile exists
        if not Profile.objects.filter(id=profile_id).exists():
            return Response({"error": "Profile does not exist"},status=status.HTTP_400_BAD_REQUEST)
        viewed_obj, created = ViewdProfile.objects.get_or_create(user=user,defaults={"profile_ids": [profile_id]})
        if not created:
            if profile_id not in viewed_obj.profile_ids:
                viewed_obj.profile_ids.append(profile_id)
                viewed_obj.save()
        return Response(
            {
                "message": "Profile viewed successfully",
                "profile_ids": viewed_obj.profile_ids
            },
            status=status.HTTP_200_OK
        )

class SavedProfilesAllView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            company_user = CompanyUser.objects.get(user=request.user)
            saved_profiles = SaveProf.objects.filter(
                user=company_user
            ).select_related("profile").order_by("-saved_at")
            serializer = SavedProfileSerializer(saved_profiles, many=True)

            return Response(serializer.data)

        except CompanyUser.DoesNotExist:
            return Response(
                {"error": "Company user not found"},
                status=404
            )

class RemoveSavedProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id):
        try:
            company_user = CompanyUser.objects.get(user=request.user)
            saved_profile = SaveProf.objects.get(
                id=id,
                user=company_user
            )
            saved_profile.delete()
            return Response(
                {"message": "Saved profile removed successfully"},
                status=status.HTTP_200_OK
            )
        except CompanyUser.DoesNotExist:
            return Response(
                {"error": "Company user not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except SaveProf.DoesNotExist:
            return Response(
                {"error": "Saved profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
