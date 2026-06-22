from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile, Experience, Education, Certificate, Skill, SavedJob
from employeer.models import JobPosting
from employeer.serializers import JobPostingSerializer
from master.models import Currency, Country,State, City
from  master.serializers import CountrySerializer, StateSerializer, CitySerializer, CurrencySerializer, MajorCategorySerializer, MajorSerializer

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    country_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    class Meta:
        model = User
        fields = ('full_name', 'email', 'password', 'mobile_number', 'work_status', 'receive_promotions', 'country_id','mobile_code')

    def create(self, validated_data):
        country_id = validated_data.pop('country_id', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.username = validated_data['email']
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ExperienceSerializer(serializers.ModelSerializer):
    # location = CountrySerializer(read_only=True)
    # location_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    start_date = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"], required=False, allow_null=True)
    end_date = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"], required=False, allow_null=True)
    class Meta:
        model = Experience
        fields = '__all__'
        read_only_fields = ['profile']

class EducationSerializer(serializers.ModelSerializer):
    education_detail = MajorCategorySerializer(source='education', read_only=True)
    course_detail = MajorSerializer(source='course', read_only=True)
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['profile']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = ['profile']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ['profile']

# class ProfileSerializer(serializers.ModelSerializer):
#     country = CountrySerializer(read_only=True)
#     state = StateSerializer(read_only=True)
#     city = CitySerializer(read_only=True)
#     current_currency = CurrencySerializer(read_only=True)
#     expected_currency = CurrencySerializer(read_only=True)
#     country_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
#     state_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
#     city_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
#     current_currency_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
#     expected_currency_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

#     experiences = ExperienceSerializer(many=True, required=False)
#     educations = EducationSerializer(many=True, required=False)
#     certifications = CertificateSerializer(many=True, required=False)
#     skills = SkillSerializer(many=True, required=False)
#     resume = serializers.FileField(required=False)
#     date_of_birth = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])


#     class Meta:
#         model = Profile
#         fields = '__all__'
#         read_only_fields = ['user']

#     def create(self, validated_data):
#         user = self.context['request'].user
#         certifications = validated_data.pop('certifications', [])
#         experiences = validated_data.pop('experiences', [])
#         educations = validated_data.pop('educations', [])
#         skills = validated_data.pop('skills', [])

#         profile = Profile.objects.create(user=user, **validated_data)

#         for cert in certifications:
#             Certificate.objects.create(profile=profile, **cert)
#         for exp in experiences:
#             Experience.objects.create(profile=profile, **exp)
#         for edu in educations:
#             Education.objects.create(profile=profile, **edu)
#         for skill in skills:
#             Skill.objects.create(profile=profile, **skill)
#         return profile

#     def update(self, instance, validated_data):
#         experiences = validated_data.pop('experiences', [])
#         educations = validated_data.pop('educations', [])
#         certifications = validated_data.pop('certifications', [])
#         skills = validated_data.pop('skills', [])

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
            
#         instance.save()
#         instance.experiences.all().delete()
#         instance.educations.all().delete()
#         instance.certifications.all().delete()
#         instance.skills.all().delete()

#         for cert in certifications:
#             Certificate.objects.create(profile=instance, **cert)
#         for exp in experiences:
#             Experience.objects.create(profile=instance, **exp)
#         for edu in educations:
#             Education.objects.create(profile=instance, **edu)
#         for skill in skills:
#             Skill.objects.create(profile=instance, **skill)

#         return instance
    
class ProfileSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    current_currency = CurrencySerializer(read_only=True)
    expected_currency = CurrencySerializer(read_only=True)
    country_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    state_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    city_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    current_currency_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    expected_currency_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    experiences = ExperienceSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    certifications = CertificateSerializer(many=True, required=False)
    skills = SkillSerializer(many=True, required=False)
    resume = serializers.FileField(required=False)
    date_of_birth = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])


    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        certifications = validated_data.pop('certifications', [])
        experiences = validated_data.pop('experiences', [])
        educations = validated_data.pop('educations', [])
        skills = validated_data.pop('skills', [])

        profile = Profile.objects.create(user=user, **validated_data)

        for cert in certifications:
            Certificate.objects.create(profile=profile, **cert)
        for exp in experiences:
            Experience.objects.create(profile=profile, **exp)
        for edu in educations:
            Education.objects.create(profile=profile, **edu)
        for skill in skills:
            Skill.objects.create(profile=profile, **skill)
        return profile

    def update(self, instance, validated_data):

        experiences = validated_data.pop("experiences", None)
        educations = validated_data.pop("educations", None)
        certifications = validated_data.pop("certifications", None)
        skills = validated_data.pop("skills", None)

        country_id = validated_data.pop("country_id", None)
        state_id = validated_data.pop("state_id", None)
        city_id = validated_data.pop("city_id", None)
        current_currency_id = validated_data.pop("current_currency_id", None)
        expected_currency_id = validated_data.pop("expected_currency_id", None)

        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Foreign Keys
        if country_id:
            instance.country = Country.objects.get(id=country_id)

        if state_id:
            instance.state = State.objects.get(id=state_id)

        if city_id:
            instance.city = City.objects.get(id=city_id)

        if current_currency_id:
            instance.current_currency = Currency.objects.get(
                id=current_currency_id
            )

        if expected_currency_id:
            instance.expected_currency = Currency.objects.get(
                id=expected_currency_id
            )

        instance.save()

        # Experiences
        if experiences is not None:
            instance.experiences.all().delete()

            for exp in experiences:
                Experience.objects.create(
                    profile=instance,
                    **exp
                )

        # Educations
        if educations is not None:
            instance.educations.all().delete()

            for edu in educations:
                Education.objects.create(
                    profile=instance,
                    **edu
                )

        # Certifications
        if certifications is not None:
            instance.certifications.all().delete()

            for cert in certifications:
                Certificate.objects.create(
                    profile=instance,
                    **cert
                )

        # Skills
        if skills is not None:
            instance.skills.all().delete()

            for skill in skills:
                Skill.objects.create(
                    profile=instance,
                    **skill
                )

        return instance
    

class SavedJobSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = SavedJob
        fields = ["id", "user", "job", "job_title", "saved_at"]
        read_only_fields = ["user", "saved_at"]

    def validate_job(self, value):
        if not JobPosting.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Job does not exist.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        job = validated_data["job"]
        saved, created = SavedJob.objects.get_or_create(user=user, job=job)
        if not created:
            raise serializers.ValidationError("Already saved.")
        return saved


class SavedJobListSerializer(serializers.ModelSerializer):
    job = JobPostingSerializer(read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = SavedJob
        fields = ["id", "job", "job_title", "saved_at"]
        read_only_fields = ["job", "job_title", "saved_at"]
