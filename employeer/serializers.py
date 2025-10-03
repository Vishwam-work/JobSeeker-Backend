# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CompanyUser
from master.serializers import CountrySerializer,JobCategorySerializer

User = get_user_model()
class CompanyUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CompanyUser
        exclude = ['user']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')

        user = User.objects.create_user(username=email, email=email, password=password)
        company_user = CompanyUser.objects.create(user=user, **validated_data)
        return company_user

class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

from rest_framework import serializers
from .models import JobPosting

class JobPostingSerializer(serializers.ModelSerializer):
    company_user = serializers.ReadOnlyField(source='company_user.id')
    location = CountrySerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    class Meta:
        model = JobPosting
        fields = [
            'id', 'company_user', 'title', 'category', 'job_title', 'company',
            'location', 'experience', 'salary', 'job_type', 'work_mode',
            'vacancies', 'application_deadline', 'description', 'requirements',
            'benefits', 'skills', 'is_urgent', 'is_remote','questions' ,'created_at', 'updated_at','status'
        ]
        read_only_fields = ('company_user', 'created_at', 'updated_at')
