from django.contrib import admin
from .models import CompanyUser, JobPosting, Application, Answer

@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'contact_person_name',
        'phone',
        'company_type',
        'industry',
    )
    search_fields = (
        'company_name',
        'contact_person_name',
        'phone',
        'email'
    )
    list_filter = (
        'company_type',
        'industry',
    )
    readonly_fields = ('user',)

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Company Info', {
            'fields': ('company_name', 'company_type', 'industry', 'company_size', 'website', 'description')
        }),
        ('Contact Info', {
            'fields': ('contact_person_name', 'designation', 'phone',)
        }),
        ('Address', {
            'fields': ('address', 'country', 'state', 'city', 'pincode')
        }),
        ('Agreements', {
            'fields': ('agree_marketing', 'agree_terms')
        }),
    )
@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    raw_id_fields = ['company_user', 'category' ,'job_title' ,'location' ,'currency']
    list_display = ('title', 'company', 'location', 'experience', 'salary', 'is_urgent', 'is_remote', 'location' ,'currency')

@admin.register(Application)
class Applications(admin.ModelAdmin):
    raw_id_fields  = ['user', 'job']
    list_display = ( 'user', 'job', 'applied_at')

@admin.register(Answer)
class Answer(admin.ModelAdmin):
    raw_id_fields  = ['user', 'job']
    list_display = ( 'user', 'job', 'question_index' ,'answer_text')