
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
 
class RetriveEmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = "__all__"
        

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"
        

class TagAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')

class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        
class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = ('__all__')
        
# Dashboard
class JobUpdateSerializer(serializers.ModelSerializer):
    employer_id = serializers.CharField(required=False, allow_blank=True)
    job_type_id = serializers.CharField(required=False, allow_blank=True)
    country_id = serializers.CharField(required=False, allow_blank=True)
    tag = TagSerializer(required=False, many=True)
    # #
    # title = serializers.CharField(required=True)
    # hirer_number = serializers.IntegerField(required=True)
    # description = serializers.CharField(required=True)
    # salary = serializers.IntegerField(required=True)
    # currency = serializers.CharField(required=True)
    # web_link = serializers.CharField(required=True)
    # view_number = serializers.IntegerField(required=True)
    # start_time = serializers.DateTimeField(required=True)
    # end_time = serializers.DateTimeField(required=True)
    class Meta:
        model = Job
        fields = ('employer_id', 'job_type_id', 'country_id', 'tag', 'title',
                  'hirer_number', 'description', 'salary', 'currency', 'web_link',
                  'view_number', 'start_time', 'end_time', 'created_at', 'updated_at', )
        
    # Get current user login
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def tag_new(self):
        tags = self.validated_data.pop('tag', None)
        if (tags):
            for tag in tags:
                try:
                    Tag.objects.get(name=tag["name"])
                except:
                    Tag.objects.create(name=tag["name"])
        return True

    def job_type_exists(self):
        try:
            JobType.objects.get(pk=self.validated_data["job_type_id"])
            return True
        except: return False
        
    def country_exists(self):
        try:
            Country.objects.get(pk=self.validated_data["country_id"])
            return True
        except: return False
        
        
    def update_tags(self, tags):
        tag_ids = []
        for tag in tags:
            obj = Tag.objects.get(pk=tag.get('id'))
            obj.name = tag.get('name')
            obj.save()
            tag_ids.append(obj.pk)
        return tag_ids
    
    def update(self, instance, validated_data):
        # instance.model_method() # call model method for instance level computation
        # # call super to now save modified instance along with the validated data
        # return super().update(instance, validated_data)  
        tag = self.initial_data.get('tag', [])
        instance.tag.set(self.update_tags(tag))
        fields = ['job_type_id', 'country_id', 'title', 'hirer_number', 'description', 'salary',
                  'currency', 'web_link', 'start_time', 'end_time']
        for field in fields:
            try:
                setattr(instance, field, validated_data[field])
            except KeyError:  # validated_data may not contain all fields during HTTP PATCH
                pass
        instance.save()
        return instance

class JobSerializer(serializers.ModelSerializer):
    # title = serializers.CharField(required=True)
    # hirer_number = serializers.IntegerField(required=True)
    # description = serializers.CharField(required=True)
    # salary = serializers.IntegerField(required=True)
    # currency = serializers.CharField(required=True)
    # web_link = serializers.CharField(required=True)
    # start_time = serializers.DateTimeField(required=True)
    # end_time = serializers.DateTimeField(required=True)
    #
    # employer = serializers.CharField(required=False, allow_blank=True)
    # job_type = CountrySerializer(many=False)
    # country = CountrySerializer(many=False)
    job_type_id = serializers.CharField(required=False)
    country_id = serializers.CharField(required=False)
    tag = TagAllSerializer(required=False, many=True)
    
    class Meta:
        model = Job
        depth = 1
        fields = ("__all__")
    
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def tag_new(self, tags, job_instance):
        if (tags):
            tag_object = None
            for tag in tags:
                try:
                    tag_object = Tag.objects.get(name=tag["name"])
                except:
                    tag_object = Tag.objects.create(name=tag["name"])
                job_instance.tag.add(tag_object)
  
    def job_type_exists(self):
        try:
            JobType.objects.get(id=self.validated_data["job_type_id"])
            return True
        except: return False
        
    def country_exists(self):
        try:
            Country.objects.get(id=self.validated_data["country_id"])
            return True
        except: return False
  
    def create(self, validated_data):
        try: 
            current_user = self._current_user()
            if not (current_user.is_staff):
                return serializers.ValidationError("User is not employer")
            else:
                # Field is names tag (source path) so you should use this name when you fetch tags from validated data:
                # Otherwise tag is still in validated_data and Job.objects.create() raises the error.
                tags = validated_data.pop('tag', None)
                employer = current_user.employer
                job = Job.objects.create(employer=employer, **validated_data)
                job.save()
                # Create multiple tag
                self.tag_new(tags, job)
                return job
        except:
            return serializers.ValidationError("Bad Request")
        
class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = Tag
        fields = ("__all__")
    
    def tag_new(self, name):
        if (name):
            try:
                Tag.objects.get(name=name)
            except:
                Tag.objects.create(name=name).save()
  
    def tag_name_exists(self):
        try:
            Tag.objects.get(name=self.validated_data["name"])
            return True
        except: return False
  
    def create(self, validated_data):
        try: 
            tag = Tag.objects.create(**validated_data)
            tag.save()
            self.tag_new(validated_data['name'])
            return tag
        except:
            return serializers.ValidationError("Bad Request")
        
class CountrySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = Country
        fields = ("__all__")
    
    def country_name_exists(self):
        try:
            Country.objects.get(name=self.validated_data["name"])
            return True
        except: return False
  
    def create(self, validated_data):
        try: 
            country = Country.objects.create(**validated_data)
            country.save()
            return country
        except:
            return serializers.ValidationError("Bad Request")