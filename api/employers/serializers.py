from django.contrib.auth.models import Group, Permission, update_last_login
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, validate_email
from django.utils.text import slugify 
from django.utils.crypto import get_random_string
from django.db.models import Q
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import NullBooleanField
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import Group
# models
from .models import *
# serializers
from api.jobs.serializers import (
    JobSerializer,
)
from api.users.serializers import (
    UserSerializer, UserCustomPublicSerializer
)
from api.reviews.serializers import (ReviewCustomSerializer)
# regex
import re
# rest fw jwt settings
from rest_framework_simplejwt.settings import api_settings
# time
from django.utils import timezone
from datetime import datetime, date, time, timedelta
# custom message
from rest_framework.exceptions import APIException
from rest_framework import status

def _is_token_valid(self, access_token):
    try:
        access_token = AccessToken(access_token)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        return True
    except:
        return False

def get_user_token(self, access_token):
    try:
        access_token = AccessToken(access_token)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        return user
    except:
        return False

def unique_slugify(slug):
    unique_slug = slug + get_random_string(length=4)
    return unique_slug

class MyMessage(APIException):
    """Readers message class"""
    def __init__(self, msg, attrs):
        APIException.__init__(self, msg)
        self.status_code = attrs.get('status_code')
        self.message = msg

class EmployerUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    company_name = serializers.CharField(required=False)
    company_location = serializers.CharField(required=False)
    company_size = serializers.CharField(required=False)
    logo = serializers.ImageField(required=False)
    description = serializers.CharField(required=False)
    web_link = serializers.CharField(required=False)
    status = serializers.BooleanField(required=False)
    package_type = serializers.CharField(required=False)
    class Meta:
        model = Employer
        fields = "__all__"
        
    # Get current user login
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def update(self, instance, validated_data):
        # instance.model_method() # call model method for instance level computation
        # # call super to now save modified instance along with the validated data
        # return super().update(instance, validated_data)  
        fields = ['company_name', 'company_location', 'company_size', 'logo', 'description', 'web_link', 'package_type']
        for field in fields:
            try:
                setattr(instance, field, validated_data[field])
            except KeyError:  # validated_data may not contain all fields during HTTP PATCH
                pass
        instance.save()
        return instance

class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Employer
        depth = 1
        fields = "__all__"
    
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
 
    def employer_exists(self):
        current_user = self._current_user()
        employer = Employer.objects.filter(Q(title__iexact=self.validated_data['title']), Q(user=current_user))
        if employer:
            return False
        return True  
  
    def create(self, validated_data):
        try: 
            current_user = self._current_user()
            employer = Employer.objects.create(**validated_data)
            employer.user = current_user
            employer.save()
            return employer
        except:
            return serializers.ValidationError("Bad Request")
        return serializers.ValidationError("Server Error")
    
class PublicEmployerSerializer(serializers.ModelSerializer):
    pk = serializers.CharField(required=False)
    user = UserCustomPublicSerializer()
    employer_job = JobSerializer(many=True)
    employer_reviews = ReviewCustomSerializer(many=True)
    class Meta:
        model = Employer
        fields = "__all__"
        
class EmployerRetriveSerializer(serializers.ModelSerializer):
    pk = serializers.CharField(required=False)
    class Meta:
        model = Employer
        fields = "__all__"