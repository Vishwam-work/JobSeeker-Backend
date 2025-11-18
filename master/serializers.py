from rest_framework import serializers
from .models import Country, State, City, Company, JobCategory, JobTitle, Currency, Major, MajorCategory


class CountrySerializer(serializers.ModelSerializer):
        class Meta:
            model = Country
            fields =  '__all__'

class StateSerializer(serializers.ModelSerializer):
        class Meta:
            model = State
            fields = ['id', 'name', 'country_id']

class CitySerializer(serializers.ModelSerializer):
        class Meta:
            model = City
            fields = ['id', 'name', 'state_id', 'country_id']

class CompanySerializer(serializers.ModelSerializer):
        class Meta:
            model = Company
            fields = ['id', 'name']

class JobCategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = JobCategory
            fields = ['id', 'name']

class JobTitleSerializer(serializers.ModelSerializer):
        class Meta:
            model = JobTitle
            fields = ['id', 'title', 'category']

class CurrencySerializer(serializers.ModelSerializer):
         class Meta:
            model = Currency
            fields = ['id', 'name', 'symbol']

class MajorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MajorCategory
        fields = ["id", "name"]


class MajorSerializer(serializers.ModelSerializer):
    category = MajorCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=MajorCategory.objects.all(),
        source="category",
        write_only=True
    )
    class Meta:
        model = Major
        fields = ["id", "code", "name", "category", "category_id"]