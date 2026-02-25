from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Experience, Education, Certificate, Skill,SavedJob, EmailOTP

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'full_name', 'work_status', 'receive_promotions', 'is_staff','role']
    list_filter = ['work_status', 'receive_promotions', 'is_staff','role']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'mobile_number', 'work_status', 'receive_promotions','role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'mobile_number', 'work_status', 'receive_promotions','role')}),
    )

class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'country', 'state', 'city']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Certificate)
admin.site.register(Skill)
admin.site.register(SavedJob)
admin.site.register(EmailOTP)
