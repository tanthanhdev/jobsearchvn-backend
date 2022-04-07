
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
        user = User.objects.get(pk=user_id)
        return True
    except:
        return False

def get_user_token(self, access_token):
    try:
        access_token = AccessToken(access_token)
        user_id = access_token['user_id']
        user = User.objects.get(pk=user_id)
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
     
class CitySerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    class Meta:
        model = City
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
        

class JobAddressSerializer(serializers.ModelSerializer):
    city_id = serializers.CharField(required=False, allow_blank=True)
    city = CitySerializer(required=False)
    class Meta:
        model = JobAddress
        fields = ('__all__')
        
class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ('__all__')

# Dashboard
class JobUpdateSerializer(serializers.ModelSerializer):
    employer_id = serializers.CharField(required=False, allow_blank=True)
    job_type_id = serializers.CharField(required=False, allow_blank=True)
    country_id = serializers.CharField(required=False, allow_blank=True)
    tag = TagSerializer(required=False, many=True)
    # foreign object
    job_job_addresses = JobAddressSerializer(required=True, many=True)
    job_benefits = BenefitSerializer(required=True, many=True)
    
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

class JobRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ("__all__")

class JobSerializer(serializers.ModelSerializer):
    job_type_id = serializers.CharField(required=True)
    country_id = serializers.CharField(required=True)
    campaign_id = serializers.CharField(required=True)
    tag = TagAllSerializer(required=False, many=True)
    # foreign object
    job_job_addresses = JobAddressSerializer(required=True, many=True)
    job_benefits = BenefitSerializer(required=True, many=True)
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
            JobType.objects.get(pk=self.validated_data["job_type_id"])
            return True
        except: return False
        
    def country_exists(self):
        try:
            Country.objects.get(pk=self.validated_data["country_id"])
            return True
        except: return False
        
    def campaign_exists(self):
        try:
            Campaign.objects.get(pk=self.validated_data["campaign_id"])
            return True
        except: return False
  
    def create(self, validated_data):
        try:
            current_user = self._current_user()
            if not (current_user.is_staff):
                return serializers.ValidationError("User is not employer")
            else:
                try:
                    # Field is names cv (source path) so you should use this name when you fetch cvs from validated data:
                    # Otherwise cv is still in validated_data and Cv.objects.create() raises the error.
                    # job = Job.objects.create(employer=current_user.employer, **validated_data)
                    tags = validated_data.pop('tag', None)
                    try:
                        job = Job.objects.create(employer=current_user.employer,
                                            job_type_id=validated_data['job_type_id'],
                                            country_id=validated_data['country_id'],
                                            campaign_id=validated_data['campaign_id'],
                                            title=validated_data['title'],
                                            hirer_number=validated_data['hirer_number'],
                                            description=validated_data['description'],
                                            job_requirement=validated_data['job_requirement'],
                                            salary=validated_data['salary'],
                                            currency=validated_data['currency'],
                                            web_link=validated_data['web_link'],
                                            start_time=validated_data['start_time'],
                                            end_time=validated_data['end_time'],
                                            )
                    except Exception as e:
                        print(e)
                    job.save()
                    # Add foreign key inlines
                    job_job_addresses = validated_data.pop('job_job_addresses', None)
                    for job_job_address in job_job_addresses:
                        JobAddress.objects.create(job=job, **job_job_address)
                    job_benefits = validated_data.pop('job_benefits', None)
                    for job_benefit in job_benefits:
                        Benefit.objects.create(job=job, **job_benefit)
                    # Add or create multiple tag
                    self.tag_new(tags, job)
                    return job
                except Exception as e:
                    print(e)
        except:
            return serializers.ValidationError("Bad Request")

class CampaignSerializer(serializers.ModelSerializer):
    city_id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    position = serializers.CharField(required=True)
    city = CitySerializer(required=False)
    class Meta:
        model = Campaign
        fields = ("__all__")
    
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def city_exists(self):
        try:
            City.objects.get(pk=self.validated_data["city_id"])
            return True
        except: return False
        
    def create(self, validated_data):
        try:
            campaign = Campaign.objects.create(city_id=validated_data["city_id"],
                                                name=validated_data["name"],
                                                position=validated_data["position"])
            campaign.save()
            return campaign
        except:
            return serializers.ValidationError("Bad Request")

class CampaignUpdateSerializer(serializers.ModelSerializer):
    city_id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    position = serializers.CharField(required=False)
    is_match_cv = serializers.BooleanField(required=False)
    status = serializers.BooleanField(required=False)
    city = CitySerializer(required=False)
    class Meta:
        model = Campaign
        fields = ("__all__")
        
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

    def city_exists(self):
        try:
            if self.validated_data["city_id"]:
                try:
                    City.objects.get(pk=self.validated_data["city_id"])
                    return True
                except: return False
        except: return True
    
    def update(self, instance, validated_data):
        # instance.model_method() # call model method for instance level computation
        # # call super to now save modified instance along with the validated data
        # return super().update(instance, validated_data)  
        fields = ['city_id', 'name', 'position', 'is_match_cv', 'status',]
        for field in fields:
            try:
                setattr(instance, field, validated_data[field])
            except KeyError:  # validated_data may not contain all fields during HTTP PATCH
                pass
        instance.save()
        return instance

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
        
class CitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = City
        fields = ("__all__")
    
    def country_name_exists(self):
        try:
            City.objects.get(name=self.validated_data["name"])
            return True
        except: return False
  
    def create(self, validated_data):
        try: 
            country = City.objects.create(**validated_data)
            country.save()
            return country
        except:
            return serializers.ValidationError("Bad Request")