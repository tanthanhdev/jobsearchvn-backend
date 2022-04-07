
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
from api.jobs.serializers import JobRetriveSerializer
from api.users.serializers import (
    UserSerializer, UserCustomPublicSerializer
)
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

class MemberPkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ("pk")
        
# foreign
class EducationCustomSerializer(serializers.ModelSerializer):
    member = MemberPkSerializer(required=False)
    class Meta:
        model = Education
        fields = ('__all__')
class ExperienceCustomSerializer(serializers.ModelSerializer):
    member = MemberPkSerializer(required=False)
    class Meta:
        model = Experience
        fields = ('__all__')
class SkillCustomSerializer(serializers.ModelSerializer):
    member = MemberPkSerializer(required=False)
    class Meta:
        model = Skill
        fields = ('__all__')
class SocialActivityCustomSerializer(serializers.ModelSerializer):
    member = MemberPkSerializer(required=False)
    class Meta:
        model = SocialActivity
        fields = ('__all__')
class CertificateCustomSerializer(serializers.ModelSerializer):
    member = MemberPkSerializer(required=False)
    class Meta:
        model = Certificate
        fields = ('__all__')

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ('__all__')
class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ('__all__')
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('__all__')
class SocialActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialActivity
        fields = ('__all__')
class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ('__all__')

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
        employer = Member.objects.filter(pk=self.validated_data['employer_id'])
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

class SaveJobSerializer(serializers.ModelSerializer):
    job_id = serializers.CharField(required=True)
    member = MemberRetriveSerializer(required=False)
    job = JobRetriveSerializer(required=False)
    class Meta:
        model = SaveJob
        fields = ("__all__")
        
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
 
    def job_exists(self):
        job = Job.objects.filter(pk=self.validated_data['job_id'])
        if job:
            return True
        return False
    
    def save_jobs_exists(self):
        try:
            SaveJob.objects.get(Q(job_id=self.validated_data['job_id'])
                                      , Q(member=self._current_user().member))
            return True
        except:
            return False
  
    def create(self, validated_data):
        try:
            current_user = self._current_user()
            saveJob = SaveJob.objects.create(job_id=validated_data['job_id'],
                                            member=current_user.member)
            saveJob.save()
            return saveJob
        except:
            return serializers.ValidationError("Bad Request")
        return serializers.ValidationError("Server Error")

class MemberUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    avatar = serializers.ImageField(required=False)
    resume = serializers.CharField(required=False)
    salary = serializers.IntegerField(required=False)
    type = serializers.CharField(required=False)
    currency = serializers.CharField(required=False)
    birthday = serializers.DateField(required=False)
    #
    member_educations = EducationCustomSerializer(required=False, many=True)
    member_experiences = ExperienceCustomSerializer(required=False, many=True)
    member_skills = SkillCustomSerializer(required=False, many=True)
    member_social_activities = SocialActivityCustomSerializer(required=False, many=True)
    member_certificates = CertificateCustomSerializer(required=False, many=True)
    class Meta:
        model = Member
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
        instance.member_educations.all().delete()
        instance.member_experiences.all().delete()
        instance.member_skills.all().delete()
        instance.member_social_activities.all().delete()
        instance.member_certificates.all().delete()
        member_educations = validated_data.get('member_educations', [])
        aList = []
        for val in member_educations:
            val['member'] = self._current_user().member
            aList.append(Education(**val))
        Education.objects.bulk_create(aList)
        member_experiences = validated_data.get('member_experiences', [])
        aList = []
        for val in member_experiences:
            val['member'] = self._current_user().member
            aList.append(Experience(**val))
        Experience.objects.bulk_create(aList)
        member_skills = validated_data.get('member_skills', [])
        aList = []
        for val in member_skills:
            val['member'] = self._current_user().member
            aList.append(Skill(**val))
        Skill.objects.bulk_create(aList)
        member_social_activities = validated_data.get('member_social_activities', [])
        aList = []
        for val in member_social_activities:
            val['member'] = self._current_user().member
            aList.append(SocialActivity(**val))
        SocialActivity.objects.bulk_create(aList)
        member_certificates = validated_data.get('member_certificates', [])
        aList = []
        for val in member_certificates:
            val['member'] = self._current_user().member
            aList.append(Certificate(**val))
        Certificate.objects.bulk_create(aList)
        fields = ['avatar', 'resume', 'salary', 'type', 'currency', 'birthday',]
        for field in fields:
            try:
                setattr(instance, field, validated_data[field])
            except KeyError:  # validated_data may not contain all fields during HTTP PATCH
                pass
        instance.save()
        return instance

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    #
    member_educations = EducationSerializer(required=False, many=True)
    member_experiences = ExperienceSerializer(required=False, many=True)
    member_skills = SkillSerializer(required=False, many=True)
    member_social_activities = SocialActivitySerializer(required=False, many=True)
    member_certificates = CertificateSerializer(required=False, many=True)
    
    class Meta:
        model = Member
        depth = 1
        fields = "__all__"
    
 
class PublicMemberSerializer(serializers.ModelSerializer):
    pk = serializers.CharField(required=False)
    user = UserCustomPublicSerializer()
    class Meta:
        model = Member
        fields = "__all__"
