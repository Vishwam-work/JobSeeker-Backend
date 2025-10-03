from django.conf import settings
from django.db import models
from master import models as master
from job_app.models import CustomUser

STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

class CompanyUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Company Info
    company_name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    company_size = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    # Contact Info
    contact_person_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    phone_code = models.CharField(max_length=10, blank=True, null=True)

    # Address
    address = models.TextField()
    country = models.ForeignKey(master.Country, on_delete=models.SET_NULL, blank=True, null=True)
    state = models.ForeignKey(master.State, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(master.City, on_delete=models.SET_NULL, blank=True, null=True)
    pincode = models.CharField(max_length=20)

    # Agreements
    agree_marketing = models.BooleanField(default=False)
    agree_terms = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

class JobPosting(models.Model):
    company_user = models.ForeignKey(CompanyUser, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=255)
    category = models.ForeignKey(master.JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    job_title = models.ForeignKey(master.JobTitle, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.CharField(max_length=255)
    location = models.ForeignKey(master.City, on_delete=models.SET_NULL, null=True, blank=True)
    experience = models.CharField(max_length=50)
    currency = models.ForeignKey(master.Currency, on_delete=models.SET_NULL, blank=True, null=True, related_name="currency")
    salary = models.CharField(max_length=50, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=[
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship')
    ])
    work_mode = models.CharField(max_length=50, choices=[
        ('office', 'Work from Office'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid')
    ], blank=True, null=True)

    vacancies = models.PositiveIntegerField(default=1)
    application_deadline = models.DateField(blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    is_urgent = models.BooleanField(default=False)
    is_remote = models.BooleanField(default=False)
    questions = models.JSONField(default=list, blank=True)
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')


    def __str__(self):
        return self.title

class Answers(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="answers")
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="answers")
    question_index = models.PositiveIntegerField()
    answer_text = models.TextField()
    class Meta:
        unique_together = ('user', 'job', 'question_index')