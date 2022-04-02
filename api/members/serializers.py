
from django.contrib.auth.models import Group, Permission, update_last_login
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, validate_email
from django.utils.text import slugify 
from django.utils.crypto import get_random_string
from django.db.models import Q
from rest_framework import serializers
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
from api.users.serializers import UserCustomPublicSerializer
from api.employers.serializers import EmployerRetriveSerializer
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
 
class MemberCustomPublicSerializer(serializers.ModelSerializer):
    user = UserCustomPublicSerializer()
    class Meta:
        model = Member
        depth = 1
        fields = ("__all__")
        
class MemberRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ("__all__")

class FollowSerializer(serializers.ModelSerializer):
    employer_id = serializers.CharField(required=True)
    member = MemberRetriveSerializer(required=False)
    employer = EmployerRetriveSerializer(required=False)
    class Meta:
        model = Follow
        fields = ("__all__")
        
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
 
    def employer_exists(self):
        employer = Employer.objects.filter(pk=self.validated_data['employer_id'])
        if employer:
            return True
        return False
    
    def follow_exists(self):
        try:
            Follow.objects.get(Q(employer_id=self.validated_data['employer_id'])
                                      , Q(member=self._current_user().member))
            return True
        except:
            return False
  
    def create(self, validated_data):
        try:
            current_user = self._current_user()
            follow = Follow.objects.create(employer_id=validated_data['employer_id'],
                                            member=current_user.member)
            follow.save()
            return follow
        except:
            return serializers.ValidationError("Bad Request")
        return serializers.ValidationError("Server Error")