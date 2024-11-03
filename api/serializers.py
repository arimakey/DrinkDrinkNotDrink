from rest_framework import serializers
from .models import UserSession, SuccessfulCase, NegativeRecommendation
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ['user', 'question_index', 'preferences', 'completed', 'recommendation']

class SuccessfulCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessfulCase
        fields = ['intensity', 'flavor_profile', 'drink_type', 'recommendation']

class NegativeRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegativeRecommendation
        fields = ['intensity', 'flavor_profile', 'drink_type', 'recommendation']
