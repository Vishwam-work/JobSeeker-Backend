from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile, Experience, Education, Certificate, Skill,Application
from master.models import Currency
from  master.serializers import CountrySerializer, StateSerializer, CitySerializer, JobCategorySerializer, JobTitleSerializer, CurrencySerializer

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password', 'mobile_number', 'work_status', 'receive_promotions')

    def create(self, validated_data):
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
    location = CountrySerializer(read_only=True)

    class Meta:
        model = Experience
        fields = '__all__'
        read_only_fields = ['profile']

class EducationSerializer(serializers.ModelSerializer):
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

class ProfileSerializer(serializers.ModelSerializer):

    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)

    current_currency = CurrencySerializer(read_only=True)
    expected_currency = CurrencySerializer(read_only=True)

    experiences = ExperienceSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    certifications = CertificateSerializer(many=True, required=False)
    skills = SkillSerializer(many=True, required=False)
    resume = serializers.FileField(required=False)

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
        experiences = validated_data.pop('experiences', [])
        educations = validated_data.pop('educations', [])
        certifications = validated_data.pop('certifications', [])
        skills = validated_data.pop('skills', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.experiences.all().delete()
        instance.educations.all().delete()
        instance.certifications.all().delete()
        instance.skills.all().delete()

        for cert in certifications:
            Certificate.objects.create(profile=instance, **cert)
        for exp in experiences:
            Experience.objects.create(profile=instance, **exp)
        for edu in educations:
            Education.objects.create(profile=instance, **edu)
        for skill in skills:
            Skill.objects.create(profile=instance, **skill)

        return instance

class ApplicationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id", "job", "user", "cover_letter", "resume", "status", "applied_at",
            "user_name", "user_email", "job_title"
        ]
        read_only_fields = ["user", "status"]