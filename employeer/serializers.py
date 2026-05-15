# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import CompanyUser,JobPosting,Answer, Application
from job_app.models import Profile
from master.serializers import CountrySerializer,JobCategorySerializer,CurrencySerializer
from master.models import JobCategory,Country,Currency
from rest_framework import serializers
from .models import JobPosting,SaveProf,ViewdProfile,Company
from master import models as master


User = get_user_model()
class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'

class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    

class CompanyUserSerializer(serializers.ModelSerializer):

    # USER FIELDS
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    # COMPANY FIELDS
    company_name = serializers.CharField(write_only=True)
    company_type = serializers.CharField(write_only=True)
    industry = serializers.CharField(write_only=True)
    company_size = serializers.CharField(write_only=True)

    website = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )

    description = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )

    address = serializers.CharField(write_only=True)

    country = serializers.PrimaryKeyRelatedField(
        queryset=master.Country.objects.all(),
        write_only=True
    )

    state = serializers.PrimaryKeyRelatedField(
        queryset=master.State.objects.all(),
        write_only=True
    )

    city = serializers.PrimaryKeyRelatedField(
        queryset=master.City.objects.all(),
        write_only=True
    )

    pincode = serializers.CharField(write_only=True)

    agree_marketing = serializers.BooleanField(default=False)
    agree_terms = serializers.BooleanField(default=False)

    # RESPONSE COMPANY DATA
    company = CompanySerializer(read_only=True)

    class Meta:
        model = CompanyUser

        fields = [
            # USER
            'id',
            'email',
            'password',
            'confirm_password',

            # COMPANY
            'company_name',
            'company_type',
            'industry',
            'company_size',
            'website',
            'description',
            'address',
            'country',
            'state',
            'city',
            'pincode',
            'agree_marketing',
            'agree_terms',

            # COMPANY USER
            'role',
            'contact_person_name',
            'designation',
            'phone',
            'phone_code',
            'is_verified',

            # RESPONSE
            'company',
        ]

        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }

    # VALIDATE PASSWORD
    def validate(self, data):

        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "password": "Passwords do not match"
            })

        return data

    # CREATE
    def create(self, validated_data):

        # -------------------------
        # USER DATA
        # -------------------------

        email = validated_data.pop('email')
        password = validated_data.pop('password')

        validated_data.pop('confirm_password')

        # -------------------------
        # COMPANY DATA
        # -------------------------

        company_data = {

            'company_name': validated_data.pop('company_name'),
            'company_type': validated_data.pop('company_type'),
            'industry': validated_data.pop('industry'),
            'company_size': validated_data.pop('company_size'),

            'website': validated_data.pop('website', ''),
            'description': validated_data.pop('description', ''),

            'address': validated_data.pop('address'),

            'country': validated_data.pop('country'),
            'state': validated_data.pop('state'),
            'city': validated_data.pop('city'),

            'pincode': validated_data.pop('pincode'),

            'agree_marketing': validated_data.pop(
                'agree_marketing',
                False
            ),

            'agree_terms': validated_data.pop(
                'agree_terms',
                False
            ),
        }

        # -------------------------
        # CREATE AUTH USER
        # -------------------------

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        user.role = 'employer'
        user.save()

        # -------------------------
        # CREATE COMPANY
        # -------------------------

        company = Company.objects.create(**company_data)

        # -------------------------
        # CREATE COMPANY USER
        # -------------------------

        company_user = CompanyUser.objects.create(
            user=user,
            company=company,
            role='employer',
            **validated_data
        )

        return company_user
# class CompanyUserSerializer(serializers.ModelSerializer):
#     company = CompanySerializer(read_only=True)
#     email = serializers.EmailField()
#     password = serializers.CharField()
#     confirm_password = serializers.CharField()

#     class Meta:
#         model = CompanyUser
#         fields = [
#             'user',
#             'email',
#             'password',
#             'confirm_password',
#             'role',
#             'contact_person_name',
#             'designation',
#             'phone',
#             'phone_code',
#             'is_verified',
#             'company',
#         ]

#     # VALIDATION
#     def validate(self, data):
#         print(data)
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError(
#                 {"password": "Passwords do not match"}
#             )

#         return data

#     # CREATE
#     def create(self, validated_data):

#         # USER DATA
#         email = validated_data.pop('email')
#         password = validated_data.pop('password')
#         validated_data.pop('confirm_password')

#         # COMPANY DATA
#         company_data = {
#             'company_name': validated_data.pop('company_name'),
#             'company_type': validated_data.pop('company_type'),
#             'industry': validated_data.pop('industry'),
#             'company_size': validated_data.pop('company_size'),
#             'website': validated_data.pop('website', ''),
#             'description': validated_data.pop('description', ''),
#             'address': validated_data.pop('address'),
#             'country': validated_data.pop('country'),
#             'state': validated_data.pop('state'),
#             'city': validated_data.pop('city'),
#             'pincode': validated_data.pop('pincode'),
#             'agree_marketing': validated_data.pop('agree_marketing', False),
#             'agree_terms': validated_data.pop('agree_terms', False),
#         }

#         # CREATE USER
#         user = User.objects.create_user(
#             username=email,
#             email=email,
#             password=password
#         )


#         # CREATE COMPANY
#         company = Company.objects.create(**company_data)

#         # CREATE COMPANY USER
#         company_user = CompanyUser.objects.create(user=user,company=company,role='employer',**validated_data)

#         return company_user

# class CompanyUserSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(write_only=True)
#     password = serializers.CharField(write_only=True)
#     confirm_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = CompanyUser
#         exclude = ['user']

#     def validate(self, data):
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError("Passwords do not match")
#         return data

#     def create(self, validated_data):
#         email = validated_data.pop('email')
#         password = validated_data.pop('password')
#         validated_data.pop('confirm_password')

#         user = User.objects.create_user(username=email, email=email, password=password)
#         company_user = CompanyUser.objects.create(user=user, **validated_data)
#         return company_user
    
class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class CompanyUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        exclude = ['user']


class JobPostingSerializer(serializers.ModelSerializer):
    company_user = CompanyUserSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    questions = serializers.JSONField(required=False)
    currency_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    application_deadline = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])

    class Meta:
        model = JobPosting
        fields = '__all__'
        read_only_fields = ('company_user', 'created_at', 'updated_at')

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'job', 'question_index', 'answer_text']
        read_only_fields = ['id']

    def validate(self, attrs):
        user = self.context['request'].user
        job = attrs['job']
        question_index = attrs['question_index']

        # Check if question index is valid for this job
        if question_index >= len(job.questions):
            raise serializers.ValidationError("Invalid question index for this job.")

        # Prevent duplicates
        if Answer.objects.filter(user=user, job=job, question_index=question_index).exists():
            raise serializers.ValidationError("You have already submitted an answer for this question.")

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ApplicationAnswerItemSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(allow_blank=True)

class ApplicationSubmitSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    answers = ApplicationAnswerItemSerializer(many=True, required=False)

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        try:
            job = JobPosting.objects.get(id=attrs['job_id'])
        except JobPosting.DoesNotExist:
            raise serializers.ValidationError({"job_id": "Job not found"})

        # Prevent duplicate application
        if Application.objects.filter(user=user, job=job).exists():
            raise serializers.ValidationError("You have already applied to this job.")

        # Validate answers: if job has questions, ensure all answered
        job_questions = list(job.questions or [])
        provided = attrs.get('answers') or []
        if len(job_questions) > 0:
            if len(provided) != len(job_questions):
                raise serializers.ValidationError("Please answer all questions before submitting.")

            # Optionally verify mapping by text presence
            job_question_set = set(job_questions)
            for item in provided:
                if item['question'] not in job_question_set:
                    raise serializers.ValidationError({"answers": f"Unknown question: {item['question']}"})

        attrs['job'] = job
        attrs['user'] = user
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = validated_data['user']
        job = validated_data['job']
        answers = validated_data.get('answers') or []

        application = Application.objects.create(user=user, job=job)
        
        
        if answers:
            # Map question text to index
            question_to_index = {q: idx for idx, q in enumerate(job.questions or [])}
            answer_objects = []
            for item in answers:
                question_text = item.get('question')
                answer_text = item.get('answer', '')
                if question_text in question_to_index:
                    answer_objects.append(
                        Answer(
                            user=user,
                            job=job,
                            question_index=question_to_index[question_text],
                            answer_text=answer_text
                        )
                    )
            if answer_objects:
                Answer.objects.bulk_create(answer_objects, ignore_conflicts=True)

        return application

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "job": instance.job.id,
            "applied_at": instance.applied_at,
            "message": "Application submitted successfully"
        }

class ApplicationListAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            'question_index',
            'answer_text',
        ]

class ApplicationListItemSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    answers = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['id', 'job', 'job_title', 'user', 'user_email', 'applied_at', 'answers', 'profile', 'application_status']

    def get_answers(self, obj):
        answers = Answer.objects.filter(user=obj.user, job=obj.job).order_by('question_index')
        job_questions = list(obj.job.questions or [])
        # Enrich with question text
        enriched = []
        for a in answers:
            q_text = job_questions[a.question_index] if a.question_index < len(job_questions) else None
            enriched.append({
                'question_index': a.question_index,
                'question_text': q_text,
                'answer_text': a.answer_text,
            })
        return enriched

    def get_profile(self, obj):
        profile = Profile.objects.filter(user=obj.user).first()
        if not profile:
            return None
        # skills
        skills = list(profile.skills.values_list('name', flat=True)) if hasattr(profile, 'skills') else []
        # experiences
        experiences = []
        if hasattr(profile, 'experiences'):
            for exp in profile.experiences.all().order_by('-start_date'):
                experiences.append({
                    'company': exp.company,
                    'role': exp.job_title,
                    'start_date': exp.start_date,
                    'end_date': exp.end_date,
                    'description': exp.description,
                    'category': exp.category,
                    'location': exp.location
                })
        # educations
        educations = []
        if hasattr(profile, 'educations'):
            for edu in profile.educations.all().order_by('-start_year'):
                educations.append({
                    'education': getattr(edu.education, 'name', None),
                    'course': getattr(edu.course, 'name', None),
                    'institution': edu.institution,
                    'start_year': edu.start_year,
                    'end_year': edu.end_year,
                    'grade': getattr(edu, 'percentage', None),
                    'score_type': edu.score_type,
                    'course_type': edu.course_type,
                })
        # certifications
        certifications = []
        if hasattr(profile, 'certifications'):
            for cert in profile.certifications.all().order_by('-year'):
                certifications.append({
                    'name': cert.name,
                    'issuer': cert.issuer,
                    'year': cert.year,
                })

        return {
            'full_name': profile.full_name,
            'email': profile.email,
            'phone': profile.phone,
            'phone_code': profile.phone_code,
            'experience': profile.experience,
            'gender': profile.gender,
            'resume': profile.resume.url if profile.resume else None,
            'country': getattr(profile.country, 'name', None),
            'state': getattr(profile.state, 'name', None),
            'city': getattr(profile.city, 'name', None),
            'skills': skills,
            'experiences': experiences,
            'educations': educations,
            'certifications': certifications,
            'professional_summary': profile.professional_summary,
            'profile_image': profile.profile_image.url if profile.profile_image else None,
        }



class CompanyListSerializer(serializers.ModelSerializer):
    job_count = serializers.SerializerMethodField()
    country = serializers.CharField(source='country.name', read_only=True)
    state = serializers.CharField(source='state.name', read_only=True)
    city = serializers.CharField(source='city.name', read_only=True)
    class Meta:
        model = CompanyUser
        fields = '__all__'

    def get_job_count(self, obj):
        return obj.job_postings.filter(status='active').count()

class CompanyDetailSerializer(serializers.ModelSerializer):
    job_postings = JobPostingSerializer(many=True, read_only=True)
    country = serializers.CharField(source='country.name', read_only=True)
    state = serializers.CharField(source='state.name', read_only=True)
    city = serializers.CharField(source='city.name', read_only=True)
    class Meta:
        model = CompanyUser
        fields = "__all__"

class ApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id','application_status']

class InterviewScheduleSerializer(serializers.ModelSerializer):
    interview_date = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"], required=False, allow_null=True)
    class Meta:
        model = Application
        fields = [
            "interview_date",
            "interview_time",
            "interview_mode",
            "meet_link",
            "notes",
            "application_status",
            "timezone"
        ]



class AppliedJobSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    job = JobPostingSerializer(read_only=True)
    class Meta:
        model = Application
        fields = [
            'id',
            'job_title',
            'company_name',
            'application_status',
            'applied_at',
            'interview_date',
            'interview_time',
            'interview_mode',
            'meet_link',
            'notes',
            'job'
        ]


    

# class ViewdprofileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ViewdProfile
#         fields = '__all__'
#         read_only_fields = ["user","viwed_at"]

#     def validate_profile(self,value):
#         if not Profile.objects.filter(id=value.id).exists():
#             raise serializers.ValidationError("Profile deos not exist")
#     def create(self, validated_data):
#         user = self.context["request"].user
#         profile_ids = validated_data["profile_ids"]
#         viewd, created = ViewdProfile.objects.get_or_create(user=user, profile_ids=profile_ids)

#         if not created:
#             raise serializers.ValidationError("Profile already viewed.")
#         return viewd

class SimpleprofileSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source='country.name', read_only=True)
    state = serializers.CharField(source='state.name', read_only=True)
    city = serializers.CharField(source='city.name', read_only=True)
    class Meta:
        model = Profile
        fields = '__all__'
class SavedProfileSerializer(serializers.ModelSerializer):
    profile = SimpleprofileSerializer(read_only=True)
    
    class Meta:
        model = SaveProf
        fields = '__all__'

class ViewdprofileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ViewdProfile
        fields = "__all__"
        read_only_fields = ["user", "viwed_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        new_profile_id = validated_data.get("profile_ids")

        # check profile exists
        if not Profile.objects.filter(id=new_profile_id).exists():
            raise serializers.ValidationError({"profile_ids": "Profile does not exist"})

        # get existing viewed data
        viewed_obj, created = ViewdProfile.objects.get_or_create(
            user=user,
            defaults={"profile_ids": [new_profile_id]})

        # if already exists
        if not created:
            # avoid duplicate ids
            if new_profile_id not in viewed_obj.profile_ids:
                viewed_obj.profile_ids.append(new_profile_id)
                viewed_obj.save()
        return viewed_obj



class SubUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CompanyUser

        fields = [
            'email',
            'password',
            'role',
            'contact_person_name',
            'designation',
            'phone',
            'phone_code',
        ]

    def create(self, validated_data):

        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # company passed from view
        company = self.context.get('company')

        # create auth user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        user.role = 'admin'
        user.save()

        # create company sub user
        company_user = CompanyUser.objects.create(
            user=user,
            company=company,
            role='admin',
            **validated_data
        )

        return company_user
    
class SubUserListSerializer(serializers.ModelSerializer):

    email = serializers.CharField(source='user.email', read_only=True)
    company_name = serializers.CharField(source='company.company_name',read_only=True)

    class Meta:
        model = CompanyUser
        fields = [
            'id',
            'email',
            'company_name',
            'role',
            'contact_person_name',
            'designation',
            'phone',
            'phone_code',
            'is_verified',
        ]