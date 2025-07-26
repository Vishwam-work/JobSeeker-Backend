# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CompanyUser

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