from django.contrib.auth.models import User
from django.db import models

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='session')
    question_index = models.IntegerField(default=0)
    preferences = models.JSONField(default=dict)  # Use django.db.models.JSONField
    completed = models.BooleanField(default=False)
    recommendation = models.CharField(max_length=255, null=True, blank=True)

class SuccessfulCase(models.Model):
    intensity = models.CharField(max_length=50)
    flavor_profile = models.CharField(max_length=50)
    drink_type = models.CharField(max_length=50)
    recommendation = models.CharField(max_length=255)

class NegativeRecommendation(models.Model):
    intensity = models.CharField(max_length=50)
    flavor_profile = models.CharField(max_length=50)
    drink_type = models.CharField(max_length=50)
    recommendation = models.CharField(max_length=255)
