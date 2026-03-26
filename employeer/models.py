from django.conf import settings
from django.db import models
from master import models as master
from job_app import models as job_app
import uuid

STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
APPLICATION_CHOICES=[
    ('shortlisted', 'Shortlisted'),
    ('Rejected', 'Rejected'),
    ('interview', 'Interview'),
    ('Under Review', 'Under Review'),
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

    #email verification
    is_verified = models.BooleanField()

    def __str__(self):
        return self.company_name

class JobPosting(models.Model):
    company_user = models.ForeignKey(CompanyUser, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
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
    questions = models.JSONField(default=list, null=True,blank=True)
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    applicants=models.PositiveIntegerField(default=0)
    apply_clicks=models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title
    
class Answer(models.Model):
    user = models.ForeignKey(job_app.CustomUser, on_delete=models.CASCADE, related_name='answers', null=True)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='answers')
    question_index = models.PositiveIntegerField()
    answer_text = models.TextField()

    class Meta:
        unique_together = ('user', 'job', 'question_index')  # This meta class ensures uniqueness here

    def __str__(self):
        return f"{self.user} - {self.job.title} - Q{self.question_index}"

class Application(models.Model):
    user = models.ForeignKey(job_app.CustomUser, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    application_status = models.CharField(max_length=20, choices=[
        ('shortlisted', 'shortlisted'),
        ('rejected', 'rejected'),
        ('interview_sch', 'Interview Scheduled'),
        ('under_review', 'Under Review')
    ], default='Under Review')
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.CharField(max_length=20, null=True, blank=True)  
    interview_mode = models.CharField(max_length=20, null=True, blank=True)  
    meet_link = models.CharField(max_length=255, null=True, blank=True)     
    notes = models.TextField(null=True, blank=True)  
    class Meta:
        unique_together = ('user', 'job')

class JobClickEvent(models.Model):
    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name="click_events"
    )
    request_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "request_id"],
                name="unique_job_click_event"
            )
        ]