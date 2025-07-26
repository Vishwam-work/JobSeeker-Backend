from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=255)
    iso3 = models.CharField(max_length=3, blank=True, null=True)
    iso2 = models.CharField(max_length=2, blank=True, null=True)
    numeric_code = models.CharField(max_length=10, blank=True, null=True)
    phonecode = models.CharField(max_length=10, blank=True, null=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    currency_name = models.CharField(max_length=50, blank=True, null=True)
    currency_symbol = models.CharField(max_length=10, blank=True, null=True)
    tld = models.CharField(max_length=10, blank=True, null=True)
    native = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    subregion = models.CharField(max_length=255, blank=True, null=True)
    subregion_id = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    emoji = models.CharField(max_length=10, blank=True, null=True)
    emojiU = models.CharField(max_length=50, blank=True, null=True)
    # You can also add JSONField for translations or timezones if needed.
    timezones = models.JSONField(blank=True, null=True)
    translations = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=255)
    country_id = models.ForeignKey('Country', on_delete=models.CASCADE)
    country_name = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=3, blank=True, null=True)
    state_code = models.CharField(max_length=10, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.country_id.name}"


class City(models.Model):
    name = models.CharField(max_length=100)
    state_id = models.ForeignKey('State', on_delete=models.CASCADE)
    state_code = models.CharField(max_length=10, blank=True, null=True)
    state_name = models.CharField(max_length=100, blank=True, null=True)
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    wikiDataId= models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return f"{self.name}, {self.state_id.name}"

class Company(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class JobCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name

class JobTitle(models.Model):
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='titles')
    title = models.CharField(max_length=255)
    def __str__(self):
        return self.title

class Currency(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10)
    def __str__(self):
        return self.name