from django.contrib import admin
from .models import Country, State, City, Company, JobCategory,JobTitle, Currency

admin.site.site_header = 'Master Data'
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Company)
admin.site.register (JobCategory)
admin.site.register(JobTitle)
admin.site.register (Currency)
