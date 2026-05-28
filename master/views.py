from django.shortcuts import render
from rest_framework import generics, status, viewsets, permissions, serializers
from .models import Country, State, City, Company, JobCategory, JobTitle, Currency, Major, MajorCategory, CourseMaster
from .serializers import CountrySerializer, StateSerializer, CitySerializer, CompanySerializer, JobTitleSerializer, JobCategorySerializer, CurrencySerializer, MajorSerializer, MajorCategorySerializer, CourseSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
# Create your views here.
class CountryList(generics.ListAPIView):
    serializer_class = CountrySerializer
    permission_classes  = []
    queryset = Country.objects.all()

class CountryListExperience(generics.ListAPIView):
    serializer_class = CountrySerializer
    permission_classes  = []
    def get_queryset(self):
        query = self.request.GET.get("q", None)
        if query:
            return Country.objects.filter(name__icontains=query).order_by("name")[:10]
        return Country.objects.all().order_by("name")[:10]
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
    serializer_class = CompanySerializer
    permission_classes = []

    def get_queryset(self):
        query = self.request.GET.get("q", None)

        if query:
            return Company.objects.filter(name__icontains=query).order_by("name")[:10]

        return Company.objects.all().order_by("name")




class JobCategoryList(generics.ListAPIView):
    serializer_class = JobCategorySerializer
    permission_classes  = []
    def get_queryset(self):
        query = self.request.GET.get("q", None)
        if query:
            return JobCategory.objects.filter(name__icontains=query).order_by("name")[:10]
        return JobCategory.objects.all().order_by("name")
# class JobTitleList(generics.ListAPIView):
#     serializer_class = JobTitleSerializer
#     permission_classes = []
#     def get_queryset(self):
#         q = self.request.GET.get("q")

#         if q:
#             return JobTitle.objects.filter(title__icontains=q).distinct().order_by("title")[:10]
#         return JobTitle.objects.all().distinct().order_by("title")

class JobTitleList(generics.ListAPIView):
    serializer_class = JobTitleSerializer
    permission_classes = []

    def get_queryset(self):

        q = self.request.GET.get("q", "")

        queryset = JobTitle.objects.filter(
            title__icontains=q
        ).order_by("title")

        unique_titles = []
        unique_ids = set()

        for job in queryset:

            title = job.title.lower().strip()

            if title not in unique_ids:
                unique_ids.add(title)
                unique_titles.append(job.id)

        return JobTitle.objects.filter(
            id__in=unique_titles
        ).order_by("title")
    
class CurrencyList(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes  = []

# List all category
class MajorCategoryListView(generics.ListAPIView):
    serializer_class = MajorCategorySerializer
    def get_queryset(self):
        query = self.request.GET.get("q")

        if query:
            return MajorCategory.objects.filter(name__icontains=query)[:10]

        return MajorCategory.objects.all()

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
        query = self.request.GET.get("q")

        qs = Major.objects.filter(category_id=category_id)

        if query:
            qs = qs.filter(name__icontains=query)

        return qs.order_by("name")

@api_view(["GET"])
@permission_classes([AllowAny])
def search_courses(request):
    query = request.GET.get("q", "")
    courses = CourseMaster.objects.filter(name__icontains=query)[:10]
    data = [{"id": c.id, "name": c.name} for c in courses]
    return Response(data)

@api_view(["POST"])
@permission_classes([AllowAny])
def create_course(request):
    name = request.data.get("name")

    course, created = CourseMaster.objects.get_or_create(name=name)

    return Response({
        "id": course.id,
        "name": course.name})

class CourseList(generics.ListAPIView):
    queryset = CourseMaster.objects.all()
    serializer_class = CourseSerializer
    permission_classes  = []