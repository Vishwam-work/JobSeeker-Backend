from django.shortcuts import render
from rest_framework import generics
from .models import Country, State, City, Company, JobCategory, JobTitle, Currency, Major, MajorCategory
from .serializers import CountrySerializer, StateSerializer, CitySerializer, CompanySerializer, JobTitleSerializer, JobCategorySerializer, CurrencySerializer, MajorSerializer, MajorCategorySerializer
from rest_framework.pagination import PageNumberPagination

# Create your views here.
class CountryList(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes  = []

class StateList(generics.ListAPIView):
    serializer_class = StateSerializer
    def get_queryset(self):
        country_id = self.request.query_params.get('country_id')
        if country_id is None:
            return State.objects.all()
        return State.objects.filter(country_id=country_id)
    permission_classes  = []

class CityList(generics.ListAPIView):
    serializer_class = CitySerializer

    def get_queryset(self):
        state_id = self.request.query_params.get('state')
        return City.objects.filter(state_id=state_id)

    permission_classes  = []

    class Meta:
        model = City
        fields = ['id', 'name', 'state_id', 'country_id']

class CompanyList(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes  = []

class JobCategoryList(generics.ListAPIView):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes  = []

class JobTitleList(generics.ListAPIView):
    serializer_class = JobTitleSerializer
    def get_queryset(self):
        if self.request.query_params.get('category') is None:
            return JobTitle.objects.all()
        category = self.request.query_params.get('category')
        return JobTitle.objects.filter(category=category)
    permission_classes  = []

class CurrencyList(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes  = []

# List all category
class MajorCategoryListView(generics.ListAPIView):
    queryset = MajorCategory.objects.all().order_by("name")
    serializer_class = MajorCategorySerializer

# List all the Major
class MajorListView(generics.ListAPIView):
    queryset = Major.objects.all().order_by("name")
    serializer_class = MajorSerializer

# Get a single major (by ID)
class MajorDetailView(generics.RetrieveAPIView):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer

# by major ID
class MajorsByCategoryView(generics.ListAPIView):
    serializer_class = MajorSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Major.objects.filter(category_id=category_id).order_by("name")

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 5