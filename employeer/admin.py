from django.contrib import admin
from .models import CompanyUser, JobPosting, Application, Answer, SaveProf,ViewdProfile,Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    raw_id_fields = ['country', 'state', 'city']

    list_display = (
        'company_name',
        'company_type',
        'industry',
        'company_size',
    )

    search_fields = (
        'company_name',
        'website',
    )

    list_filter = (
        'company_type',
        'industry',
    )

    fieldsets = (
        ('Company Info', {
            'fields': (
                'company_name',
                'company_type',
                'industry',
                'company_size',
                'website',
                'description',
                'company_logo',
            )
        }),

        ('Address', {
            'fields': (
                'address',
                'country',
                'state',
                'city',
                'pincode',
            )
        }),

        ('Agreements', {
            'fields': (
                'agree_marketing',
                'agree_terms',
            )
        }),
    )

@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    raw_id_fields = ['company', 'user']

    list_display = (
        'get_company_name',
        'contact_person_name',
        'phone',
        'role',
        'designation',
    )

    search_fields = (
        'contact_person_name',
        'user__email',
        'company__company_name',
    )

    list_filter = (
        'role',
        'designation',
    )

    def get_company_name(self, obj):
        return obj.company.company_name if obj.company else "No Company"

    get_company_name.short_description = "Company Name"


# @admin.register(CompanyUser)
# class CompanyUserAdmin(admin.ModelAdmin):
#     raw_id_fields = ['user', 'country', 'state', 'city']
#     list_display = (
#         'company_name',
#         'contact_person_name',
#         'phone',
#         'company_type',
#         'industry',
#     )
#     search_fields = (
#         'company_name',
#         'contact_person_name',
#         'phone',
#         'email'
#     )
#     list_filter = (
#         'company_type',
#         'industry',
#     )
#     # readonly_fields = ('user',)

#     fieldsets = (
#         ('User Info', {
#             'fields': ('user', 'is_verified')
#         }),
#         ('Company Info', {
#             'fields': ('company_name', 'company_type', 'industry', 'company_size', 'website', 'description')
#         }),
#         ('Contact Info', {
#             'fields': ('contact_person_name', 'designation', 'phone',)
#         }),
#         ('Address', {
#             'fields': ('address', 'country', 'state', 'city', 'pincode')
#         }),
#         ('Agreements', {
#             'fields': ('agree_marketing', 'agree_terms')
#         }),
#     )
@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    raw_id_fields = ['company_user' ,'currency']
    list_display = ('title', 'company', 'location', 'experience', 'salary', 'is_urgent', 'is_remote', 'location' ,'currency')

@admin.register(Application)
class Applications(admin.ModelAdmin):
    raw_id_fields  = ['user', 'job']
    list_display = ( 'user', 'job', 'applied_at')

@admin.register(Answer)
class Answer(admin.ModelAdmin):
    raw_id_fields  = ['user', 'job']
    list_display = ( 'user', 'job', 'question_index' ,'answer_text')

@admin.register(SaveProf)
class SaveProf(admin.ModelAdmin):
    raw_id_fields  = ['user', 'profile']
    list_display = ( 'user', 'profile', 'saved_at')

@admin.register(ViewdProfile)
class ViewdProfile(admin.ModelAdmin):
    raw_id_fields  = ['user']
    list_display = ( 'user', 'viwed_at')