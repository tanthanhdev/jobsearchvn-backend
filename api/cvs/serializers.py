
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
from api.members.serializers import MemberCustomPublicSerializer
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

class Cv_CareerRetriveSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Cv_Career
        fields = ('id',)
        
class Cv_CareerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = Cv_Career
        fields = ("__all__")
  
    def cvCareer_name_exists(self):
        try:
            Cv_Career.objects.get(name=self.validated_data["name"])
            return True
        except: return False
  
    def create(self, validated_data):
        try: 
            cvCareer = Cv_Career.objects.create(**validated_data)
            cvCareer.save()
            return cvCareer
        except:
            return serializers.ValidationError("Bad Request")

class Cv_DesignRetriveSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Cv_Design
        fields = ('id',)
      
class Cv_DesignSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = Cv_Design
        fields = ("__all__")
  
    def cvDesign_name_exists(self):
        try:
            Cv_Design.objects.get(name=self.validated_data["name"])
            return True
        except: return False
  
    def create(self, validated_data):
        try: 
            cvDesign = Cv_Design.objects.create(**validated_data)
            cvDesign.save()
            return cvDesign
        except:
            return serializers.ValidationError("Bad Request")

# foreign
class CvEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CvEducation
        fields = ('__all__')
class CvExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CvExperience
        fields = ('__all__')
class CvSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CvSkill
        fields = ('__all__')
class CvSocialActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CvSocialActivity
        fields = ('__all__')
class CvCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CvCertificate
        fields = ('__all__')

# Main
class CvUpdateSerializer(serializers.ModelSerializer):
    cv_career = Cv_CareerRetriveSerializer(required=False, many=True)
    cv_design = Cv_DesignRetriveSerializer(required=False, many=True)
    # #
    title = serializers.CharField(required=True)
    target_major = serializers.CharField(required=True)
    class Meta:
        model = Cv
        fields = ('cv_career', 'cv_design', 'title', 'target_major')
        
    # Get current user login
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False

    def update_cv_careers(self, cv_careers):
        cv_career_ids = []
        for cv_career in cv_careers:
            obj = Cv_Career.objects.get(pk=cv_career.get('id'))
            obj.name = cv_career.get('name')
            obj.save()
            cv_career_ids.append(obj.pk)
        return cv_career_ids
    
    def update_cv_designs(self, cv_designs):
        cv_design_ids = []
        for cv_design in cv_designs:
            obj = Cv_Design.objects.get(pk=cv_design["id"])
            obj.save()
            cv_design_ids.append(obj.pk)
        return cv_design_ids
    
    def cv_career_exists(self):
        cv_careers = self.validated_data.pop('cv_career', None)
        if (cv_careers):
            for cv_career in cv_careers:
                try:
                    Cv_Career.objects.get(pk=cv_career["id"])
                    return True
                except: return False
        else: return False
    
    def cv_design_exists(self):
        cv_designs = self.validated_data.pop('cv_design', None)
        if (cv_designs):
            for cv_design in cv_designs:
                try:
                    Cv_Design.objects.get(pk=cv_design["id"])
                    return True
                except: return False
        else: return False
    
    def update(self, instance, validated_data):
        # instance.model_method() # call model method for instance level computation
        # # call super to now save modified instance along with the validated data
        # return super().update(instance, validated_data)  
        cv_career = self.initial_data.get('cv_career', [])
        cv_design = self.initial_data.get('cv_design', [])
        instance.cv_career.set(self.update_cv_careers(cv_career))
        instance.cv_design.set(self.update_cv_designs(cv_design))
        fields = ['title', 'target_major']
        for field in fields:
            try:
                setattr(instance, field, validated_data[field])
            except KeyError:  # validated_data may not contain all fields during HTTP PATCH
                pass
        instance.save()
        return instance

class CvSerializer(serializers.ModelSerializer):
    member = MemberCustomPublicSerializer(required=False)
    cv_career = Cv_CareerRetriveSerializer(required=True, many=True)
    cv_design = Cv_DesignRetriveSerializer(required=True, many=True)
    #
    cv_cv_educations = CvEducationSerializer(many=True)
    cv_cv_experiences = CvExperienceSerializer(many=True)
    cv_cv_skills = CvSkillSerializer(many=True)
    cv_cv_social_activities = CvSocialActivitySerializer(many=True)
    cv_cv_certificates = CvCertificateSerializer(many=True)
    #
    title = serializers.CharField(required=True)
    target_major = serializers.CharField(required=True)
    class Meta:
        model = Cv
        depth = 1
        fields = ("__all__")
    
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def cv_career_add(self, cv_careers, cv_instance):
        if (cv_careers):
            cv_career_object = None
            for cv_career in cv_careers:
                try:
                    cv_career_object = Cv_Career.objects.get(pk=cv_career["id"])
                except: return False
                cv_instance.cv_career.add(cv_career_object)
                
    def cv_design_add(self, cv_designs, cv_instance):
        if (cv_designs):
            cv_design_object = None
            for cv_design in cv_designs:
                try:
                    cv_design_object = Cv_Design.objects.get(pk=cv_design["id"])
                except: return False
                cv_instance.cv_design.add(cv_design_object)
  
    def cv_career_exists(self):
        cv_careers = self.validated_data.pop('cv_career', None)
        if (cv_careers):
            for cv_career in cv_careers:
                try:
                    Cv_Career.objects.get(pk=cv_career['id'])
                    return True
                except: return False
        else: return False
  
    def cv_design_exists(self):
        cv_designs = self.validated_data.pop('cv_design', None)
        if (cv_designs):
            for cv_design in cv_designs:
                try:
                    Cv_Design.objects.get(pk=cv_design['id'])
                    return True
                except: return False
        else: return False
  
    def create(self, validated_data):
        try: 
            current_user = self._current_user()
            if not (current_user.is_active):
                return serializers.ValidationError("Account member is not activation")
            else:
                # Field is names cv (source path) so you should use this name when you fetch cvs from validated data:
                # Otherwise cv is still in validated_data and Cv.objects.create() raises the error.
                cv_careers = self.initial_data.pop('cv_career', None)
                cv_designs = self.initial_data.pop('cv_design', None)
                try:
                    cv = Cv.objects.create(member=current_user.member,
                                           title=validated_data['title'],
                                           target_major=validated_data['target_major'])
                except Exception as e:
                    print(e)
                    print('___________________________________')
                cv.save()
                # Add foreign key inlines
                cv_educations = validated_data.pop('cv_cv_educations', None)
                for cv_education in cv_educations:
                    CvEducation.objects.create(cv=cv, **cv_education)
                cv_cv_experiences = validated_data.pop('cv_cv_experiences', None)
                for cv_cv_experience in cv_cv_experiences:
                    CvExperience.objects.create(cv=cv, **cv_cv_experience)
                cv_cv_skills = validated_data.pop('cv_cv_skills', None)
                for cv_cv_skill in cv_cv_skills:
                    CvSkill.objects.create(cv=cv, **cv_cv_skill)
                cv_cv_social_activities = validated_data.pop('cv_cv_social_activities', None)
                for cv_cv_social_activity in cv_cv_social_activities:
                    CvSocialActivity.objects.create(cv=cv, **cv_cv_social_activity)
                cv_cv_certificates = validated_data.pop('cv_cv_certificates', None)
                for cv_cv_certificate in cv_cv_certificates:
                    CvCertificate.objects.create(cv=cv, **cv_cv_certificate)
                # Add multiple cv_career & cv_design
                self.cv_career_add(cv_careers, cv)
                self.cv_design_add(cv_designs, cv)
                return cv
        except:
            return serializers.ValidationError("Bad Request")
