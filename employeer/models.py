from django.conf import settings
from django.db import models
from master import models as master

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
