# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from master import models as master

class CustomUser(AbstractUser):
    WORK_STATUS_CHOICES = [
        ('fresher', 'Fresher'),
        ('experienced', 'Experienced'),

    ]

    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    work_status = models.CharField(max_length=20, choices=WORK_STATUS_CHOICES)
    receive_promotions = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=255)
    experience = models.CharField(max_length=50, blank=True)
    current_salary = models.CharField(max_length=50, blank=True)
    current_currency = models.ForeignKey(master.Currency, on_delete=models.SET_NULL, blank=True, null=True, related_name="current_currency")
    expected_salary = models.CharField(max_length=50, blank=True)
    expected_currency = models.ForeignKey(master.Currency, on_delete=models.SET_NULL, blank=True, null=True, related_name="expected_currency")
    notice_period = models.CharField(max_length=50, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    country = models.ForeignKey(master.Country, on_delete=models.SET_NULL, blank=True, null=True)
    state = models.ForeignKey(master.State, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(master.City, on_delete=models.SET_NULL, blank=True, null=True)
    phone_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name}'s Profile"

class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences', null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.ForeignKey(master.JobTitle, on_delete=models.SET_NULL, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    category = models.ForeignKey(master.JobCategory, on_delete=models.SET_NULL, blank=True, null=True)
    location = models.ForeignKey(master.Country, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return f"{self.profile.user.full_name}'s Experience"

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=255)
    field = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    percentage = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return f"{self.profile.user.full_name}'s Education"

class Certificate(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    def __str__(self):
        return f"{self.profile.user.full_name}'s Certificate"

class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.profile.user.full_name}'s Skill"
    

class SavedJob(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey("employeer.JobPosting", on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
