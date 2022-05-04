
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
from api.cvs.models import (Cv, CvEducation, CvExperience,
                            CvSkill, CvSocialActivity, CvCertificate)
# serializers
from api.users.serializers import UserCustomPublicSerializer
from api.employers.serializers import EmployerRetriveSerializer
from api.jobs.serializers import JobRetriveSerializer
from api.users.serializers import (
    UserCustomPublicSerializer
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
class FilteredCVSerializer(serializers.ListSerializer):
    
    def to_representation(self, data):
        data = data.filter(status=1)
        return super(FilteredCVSerializer, self).to_representation(data)
class CvSerializer(serializers.ModelSerializer):
    #
    cv_cv_educations = CvEducationSerializer(required=True, many=True)
    cv_cv_experiences = CvExperienceSerializer(required=True, many=True)
    cv_cv_skills = CvSkillSerializer(required=True, many=True)
    cv_cv_social_activities = CvSocialActivitySerializer(required=True, many=True)
    cv_cv_certificates = CvCertificateSerializer(required=True, many=True)
    class Meta:
        model = Cv
        list_serializer_class = FilteredCVSerializer
        fields = ('__all__')
        
    
class MemberCVsService(serializers.ModelSerializer):
    member_cvs = CvSerializer(many=True)
    user = UserCustomPublicSerializer()
    class Meta:
        model = Member
        fields = ('__all__')

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
    completion_date = serializers.DateField(required=False)
    starting_date = serializers.DateField(required=False)
    gpa = serializers.IntegerField(required=False)
    major = serializers.CharField(required=False, allow_blank=True)
    university_name = serializers.CharField(required=False, allow_blank=True)
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
    
class ApplySerializer(serializers.ModelSerializer):
    job_id = serializers.CharField(required=True)
    member = MemberCVsService(required=False)
    job = JobRetriveSerializer(required=False)
    class Meta:
        model = Apply
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
    
    def apply_exists(self):
        try:
            Apply.objects.get(Q(job_id=self.validated_data['job_id'])
                                      , Q(member=self._current_user().member))
            return True
        except:
            return False
  
    def create(self, validated_data):
        try:
            current_user = self._current_user()
            apply = Apply.objects.create(job_id=validated_data['job_id'],
                                            member=current_user.member)
            apply.save()
            return apply
        except:
            return serializers.ValidationError("Bad Request")
        return serializers.ValidationError("Server Error")

class ApplyUpdateSerializer(serializers.ModelSerializer):
    job_id = serializers.CharField(required=False)
    status = serializers.CharField(required=True)
    member = MemberRetriveSerializer(required=False)
    job = JobRetriveSerializer(required=False)
    class Meta:
        model = Apply
        fields = ("__all__")
        
    # Get current user login
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def update(self, instance, validated_data):
        fields = ['status']
        for field in fields:
            try:
                setattr(instance, field, validated_data[field])
            except KeyError:  # validated_data may not contain all fields during HTTP PATCH
                pass
        instance.save()
        return instance

class MemberUpdateSerializer(serializers.ModelSerializer):
    user = UserCustomPublicSerializer(required=False)
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
    # for user
    # address = serializers.CharField(required=False)
    # phone_number = serializers.CharField(required=False)
    # first_name = serializers.CharField(required=False)
    # last_name = serializers.CharField(required=False)
    # gender = serializers.CharField(required=False)
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
        if validated_data.get('member_educations', None) is not None:
            instance.member_educations.all().delete()
            member_educations = validated_data.get('member_educations', [])
            aList = []
            for val in member_educations:
                val['member'] = self._current_user().member
                aList.append(Education(**val))
            Education.objects.bulk_create(aList)
        if validated_data.get('member_experiences', None) is not None:
            instance.member_experiences.all().delete()
            member_experiences = validated_data.get('member_experiences', [])
            aList = []
            for val in member_experiences:
                val['member'] = self._current_user().member
                aList.append(Experience(**val))
            Experience.objects.bulk_create(aList)
        if validated_data.get('member_skills', None) is not None:
            instance.member_skills.all().delete()
            member_skills = validated_data.get('member_skills', [])
            aList = []
            for val in member_skills:
                val['member'] = self._current_user().member
                aList.append(Skill(**val))
            Skill.objects.bulk_create(aList)
        if validated_data.get('member_social_activities', None) is not None:
            instance.member_social_activities.all().delete()
            member_social_activities = validated_data.get('member_social_activities', [])
            aList = []
            for val in member_social_activities:
                val['member'] = self._current_user().member
                aList.append(SocialActivity(**val))
            SocialActivity.objects.bulk_create(aList)
        if validated_data.get('member_certificates', None) is not None:
            instance.member_certificates.all().delete()
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
        if self.initial_data.get('address', None):
            instance.user.address = self.initial_data.get('address', None)
        if self.initial_data.get('phone_number', None):
            instance.user.phone_number = self.initial_data.get('phone_number', None)
        if self.initial_data.get('first_name', None):
            instance.user.first_name = self.initial_data.get('first_name', None)
        if self.initial_data.get('last_name', None):
            instance.user.last_name = self.initial_data.get('last_name', None)
        if self.initial_data.get('gender', None):
            instance.user.gender = self.initial_data.get('gender', None)
        instance.user.save()
        instance.save()
        return instance

class MemberSerializer(serializers.ModelSerializer):
    user = UserCustomPublicSerializer()
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


class RegisterNotificationSerializer(serializers.ModelSerializer):
    member = MemberSerializer(required=False)
    #
    member_id = serializers.CharField(required=False)
    job_name = serializers.CharField(required=True)
    level = serializers.CharField(required=True)
    district = serializers.CharField(required=True)
    major = serializers.CharField(required=True)
    salary = serializers.IntegerField(required=True)
    currency = serializers.CharField(required=True)
    cron_job = serializers.CharField(required=True)
    status = serializers.BooleanField(required=False)
    
    class Meta:
        model = RegisterNotification
        depth = 1
        fields = "__all__"
        
    def _current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return False
    
    def create(self, validated_data):
        try:
            # Field is names cv (source path) so you should use this name when you fetch cvs from validated data:
            # Otherwise cv is still in validated_data and Cv.objects.create() raises the error.
            # job = Job.objects.create(employer=current_user.employer, **validated_data)
            try:
                registerJob = RegisterNotification.objects.create(**validated_data, member=self._current_user().member)
            except Exception as e:
                print('_____________________')
                print(e)
            registerJob.save()
            return registerJob
        except:
            return serializers.ValidationError("Bad Request")
        
class RegisterNotificationUpdateSerializer(serializers.ModelSerializer):
    member = MemberSerializer(required=False)
    job_name = serializers.CharField(required=False)
    level = serializers.CharField(required=False)
    district = serializers.CharField(required=False)
    major = serializers.CharField(required=False)
    salary = serializers.IntegerField(required=False)
    currency = serializers.CharField(required=False)
    cron_job = serializers.CharField(required=False)
    status = serializers.BooleanField(required=False)
    #
    class Meta:
        model = RegisterNotification
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
        fields = ['job_name', 'level', 'district', 'major', 'salary', 'currency', 'cron_job', 'status']
        for field in fields:
            try:
                setattr(instance, field, validated_data[field])
            except KeyError:  # validated_data may not contain all fields during HTTP PATCH
                pass
        instance.save()
        return instance