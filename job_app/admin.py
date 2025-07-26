from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Experience, Education, Certificate, Skill

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'full_name', 'work_status', 'receive_promotions', 'is_staff']
    list_filter = ['work_status', 'receive_promotions', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'mobile_number', 'work_status', 'receive_promotions')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'mobile_number', 'work_status', 'receive_promotions')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Certificate)
admin.site.register(Skill)