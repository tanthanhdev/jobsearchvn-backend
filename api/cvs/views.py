from functools import reduce
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User, Group, Permission
from rest_framework import viewsets
from rest_framework import status
from django.db.models import Q, query
from collections import OrderedDict
from rest_framework_simplejwt.tokens import RefreshToken

from api.employers.models import employer_upload_file

from .models import *
from api.jobs.models import Campaign, Job
from api.jobs.serializers import JobSerializer
from .serializers import CvSerializer, CvUpdateSerializer, Cv_TemplateSerializer, Cv_CareerSerializer, Cv_DesignSerializer, SaveCvSerializer
from .serializers import _is_token_valid, get_user_token
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid, IsEmployer
from operator import or_, and_
from django.core import serializers

from api.users import status_http
import operator
from api.users.custom_pagination import CustomPagination
from datetime import datetime    

class CvViewSet(viewsets.ModelViewSet):
    queryset = Cv.objects.all()
    default_serializer_classes = CvSerializer
    permission_classes = [IsAuthenticated, IsTokenValid]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Cv.objects.filter(Q(user=request.user), Q(user__is_active=True))
            serializer = CvSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv': 'Cv not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request):
        try:
            slug = request.GET.get('slug')
            queryset = Cv.objects.get(slug=slug, user=request.user, user__is_active=True)
            serializer = CvSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv': 'Cv not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = CvSerializer(data=request.data, context={
            'request': request
        })
        messages = {}
        if serializer.is_valid():
            if not serializer.cv_design_exists():
                messages['cv_design'] = "CV design not exists"
            if not serializer.cv_career_exists():
                messages['cv_career'] = "CV career not exists"
            if messages:
                return Response(messages, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)              

    def update(self, request, format=None):
        queryset = None
        try:
            slug = request.GET.get('slug')
            queryset = Cv.objects.get(Q(slug=slug), Q(user=request.user), Q(user__is_active=True))
            data = request.data
            serializer = CvUpdateSerializer(queryset, data=data, context={
                'request': request
            })
            messages = {}
            if serializer.is_valid():
                if not serializer.cv_design_exists():
                    messages['cv_design'] = "CV design not exists"
                if not serializer.cv_career_exists():
                    messages['cv_career'] = "CV career not exists"
                if messages:
                    return Response(messages, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Cv Update Not Found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, format=None):
        try:
            slug = request.GET.get('slug')
            if not slug:
                queryset = Cv.objects.filter(Q(user=request.user), Q(user__is_active=True))
                if not queryset:
                    return Response({'cv': 'Cv Not Found'}, status=status.HTTP_400_BAD_REQUEST)
                queryset.delete()
                return Response({'message': 'Delete all cv successfully'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                queryset = Cv.objects.get(Q(slug=slug), Q(user=request.user), Q(user__is_active=True))
                queryset.delete()
                return Response({'message': 'Delete cv successfully'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class CvSaveViewSet(viewsets.ModelViewSet):
    queryset = SaveCv.objects.all()
    default_serializer_classes = SaveCvSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            serializer = SaveCvSerializer(SaveCv.objects.all(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv': 'SaveCv not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, id=None):
        try:
            queryset = SaveCv.objects.get(pk=id)
            serializer = SaveCvSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv': 'SaveCv not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = SaveCvSerializer(data=request.data, context={
            'request': request
        })
        messages = {}
        if serializer.is_valid():
            if serializer.SaveCv_exists():
                messages['message'] = "Save Cv has exists"
            if messages:
                return Response(messages, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)              

    def destroy(self, request, id=None, format=None):
        try:
            if not id:
                queryset = SaveCv.objects.all()
                if not queryset:
                    return Response({'message': 'SaveCv Not Found'}, status=status.HTTP_404_NOT_FOUND)
                queryset.delete()
                return Response({'message': 'Delete all save cv successfully'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                SaveCv.objects.get(pk=id).delete()
                return Response({'message': 'Delete save cv successfully'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

# Public CV
class PublicCVViewSet(viewsets.ModelViewSet):
    queryset = Cv.objects.all()
    default_serializer_classes = CvSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
 
    def retrieve(self, request, slug=None):
        try:
            queryset = Cv.objects.get(slug=slug)
            serializer = CvSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv': 'Cv not found'}, status=status.HTTP_404_NOT_FOUND)
        
# Cv_Template Unauthenticated

class Cv_TemplateUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = Cv_Template.objects.all()
    default_serializer_classes = Cv_TemplateSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.queryset
            query_string = request.GET.get('q')
            cv_career = request.GET.get('cv_career')
            cv_design = request.GET.get('cv_design')
            state = request.GET.get('state')
            if query_string:
                query_string = query_string.strip()
                queryset = queryset.filter(Q(title__icontains=query_string) | Q(slug__icontains=query_string))
            if cv_career:
                cv_career = cv_career.strip()
                queryset = queryset.filter(Q(cv_career__id=cv_career))
            if cv_design:
                cv_design = cv_design.strip()
                queryset = queryset.filter(Q(cv_design__id=cv_design))
            if state:
                state = state.strip()
                if state == "Mới nhất":
                    queryset = queryset.order_by('-pk')
                elif state == "Dùng nhiều nhất":
                    queryset = queryset.order_by('-view')
            if queryset.count() == 0:
                return Response({'message': 'Cv_Template not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = Cv_TemplateSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv_template': 'Cv_Template not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Cv_Template.objects.get(slug=slug)
            serializer = Cv_TemplateSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv_template': 'Cv_Template not found'}, status=status.HTTP_404_NOT_FOUND)


class ViewPublicCv_TemplateViewSet(viewsets.ModelViewSet):
    queryset = Cv_Template.objects.all()
    default_serializer_classes = Cv_TemplateSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def setView(self, request, *args, **kwargs):
        if request.method == "POST":
            try:
                cv = Cv_Template.objects.get(pk=request.data.get('template_id'))
                cv.view = cv.view + 1
                cv.save()
                return Response({'message': "Updated view", 'view': cv.view}, status=status.HTTP_200_OK)
            except:
                return Response({'cv_template': 'Cv_Template not found'}, status=status.HTTP_400_BAD_REQUEST)

# Cv_Career Unauthenticated
class Cv_CareerUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = Cv_Career.objects.all()
    default_serializer_classes = Cv_CareerSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Cv_Career.objects.all()
            serializer = Cv_CareerSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv_career': 'Cv_Career not found'}, status=status.HTTP_400_BAD_REQUEST)
        
# Cv_Design Unauthenticated
class Cv_DesignUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = Cv_Design.objects.all()
    default_serializer_classes = Cv_DesignSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Cv_Design.objects.all()
            serializer = Cv_DesignSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv_design': 'Cv_Design not found'}, status=status.HTTP_400_BAD_REQUEST)

class MatchCVViewSet(viewsets.ModelViewSet):
    queryset = Cv.objects.all()
    default_serializer_classes = CvSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.queryset
            queryCampaigns = Campaign.objects.filter(employer=request.user.employer, is_match_cv=True, status=True)
            campaignNameList = []
            campaignPositionList = []
            jobTitleList = []
            jobDescriptionList = []
            jobRequirementList = []
            jobBenefitList = []
            for campaign in queryCampaigns:
                campaignNameList.append(campaign.name)
                campaignPositionList.append(campaign.position)
                jobs = campaign.campaign_jobs.all().filter(Q(is_active=True) & Q(end_time__gte=datetime.now()))
                for job in jobs:
                    jobTitleList.append(job.title)
                    jobDescriptionList.append(job.description)
                    jobRequirementList.append(job.job_requirement)
                    benefits = job.job_benefits.all()
                    for benefit in benefits:
                        jobBenefitList.append(benefit.benefit)
            # campaign search
            filterTitle_campaignName = reduce(operator.or_, (Q(title__icontains = item) for item in campaignNameList))
            filterTitle_campaignPosition = reduce(operator.or_, (Q(title__icontains = item) for item in campaignPositionList))
            filterTarget_campaignName = reduce(operator.or_, (Q(target_major__icontains = item) for item in campaignNameList))
            filterTarget_campaignPosition = reduce(operator.or_, (Q(target_major__icontains = item) for item in campaignPositionList))
            filterCvEducations_campaignName = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in campaignNameList))
            filterCvEducations_campaignPosition = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in campaignPositionList))
            filterCvExperiences_campaignName = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in campaignNameList))
            filterCvExperiences_campaignPosition = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in campaignPositionList))
            filterCvSkills_campaignName = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in campaignNameList))
            filterCvSkills_campaignPosition = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in campaignPositionList))
            filterSocialActivities_campaignName = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in campaignNameList))
            filterSocialActivities_campaignPosition = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in campaignPositionList))
            # searching jobs of campaign
            filterTitle_jobTitle = reduce(operator.or_, (Q(title__icontains = item) for item in jobTitleList))
            filterTitle_jobDescription = reduce(operator.or_, (Q(title__icontains = item) for item in jobDescriptionList))
            filterTitle_jobRequirement = reduce(operator.or_, (Q(title__icontains = item) for item in jobRequirementList))
            filterTarget_jobTitle = reduce(operator.or_, (Q(target_major__icontains = item) for item in jobTitleList))
            filterTarget_jobDescription = reduce(operator.or_, (Q(target_major__icontains = item) for item in jobDescriptionList))
            filterTarget_jobRequirement = reduce(operator.or_, (Q(target_major__icontains = item) for item in jobRequirementList))
            filterTarget_jobBenefit = reduce(operator.or_, (Q(target_major__icontains = item) for item in jobBenefitList))
            filterCvEducations_jobTitle = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in jobTitleList))
            filterCvEducations_jobDescription = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in jobDescriptionList))
            filterCvEducations_jobRequirement = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in jobRequirementList))
            filterCvExperiences_jobTitle = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in jobTitleList))
            filterCvExperiences_jobDescription = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in jobDescriptionList))
            filterCvExperiences_jobRequirement = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in jobRequirementList))
            filterCvSkills_jobTitle = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in jobTitleList))
            filterCvSkills_jobDescription = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in jobDescriptionList))
            filterCvSkills_jobRequirement = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in jobRequirementList))
            filterSocialActivities_jobTitle = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in jobTitleList))
            filterSocialActivities_jobDescription = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in jobDescriptionList))
            filterSocialActivities_jobRequirement = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in jobRequirementList))
            # final
            queryset = queryset.filter(Q(filterTitle_campaignName) | Q(filterTarget_campaignName)
                                       | Q(filterTitle_campaignPosition) | Q(filterTarget_campaignPosition)
                                       | Q(filterCvEducations_campaignName) | Q(filterCvEducations_campaignPosition)
                                       | Q(filterCvExperiences_campaignName) | Q(filterCvExperiences_campaignPosition)
                                       | Q(filterCvSkills_campaignName) | Q(filterCvSkills_campaignPosition)
                                       | Q(filterSocialActivities_campaignName) | Q(filterSocialActivities_campaignPosition)
                                       | Q(filterTitle_jobTitle) | Q(filterTitle_jobDescription)
                                       | Q(filterTitle_jobRequirement) | Q(filterTarget_jobTitle)
                                       | Q(filterTarget_jobDescription) | Q(filterTarget_jobRequirement)
                                       | Q(filterTarget_jobBenefit) | Q(filterCvEducations_jobTitle)
                                       | Q(filterCvEducations_jobDescription) | Q(filterCvEducations_jobRequirement)
                                       | Q(filterCvExperiences_jobTitle) | Q(filterCvExperiences_jobTitle)
                                       | Q(filterCvExperiences_jobDescription) | Q(filterCvExperiences_jobRequirement)
                                       | Q(filterCvSkills_jobTitle) | Q(filterCvSkills_jobDescription)
                                       | Q(filterCvSkills_jobRequirement) | Q(filterSocialActivities_jobTitle)
                                       | Q(filterSocialActivities_jobDescription) | Q(filterSocialActivities_jobRequirement)).distinct()
            if queryset.count() == 0:
                return Response({'message': 'Cv not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CvSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv': 'SaveCv not found'}, status=status.HTTP_404_NOT_FOUND)

class MatchCVCampaignViewSet(viewsets.ModelViewSet):
    queryset = Cv.objects.filter(status=1)
    default_serializer_classes = CvSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = CustomPagination
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, id=None, *args, **kwargs):
        try:
            if id:
                queryset = self.queryset
                campaign = Campaign.objects.get(employer=request.user.employer, is_match_cv=True, status=True, pk=id)
                campaignNameList = []
                campaignPositionList = []
                jobTitleList = []
                jobDescriptionList = []
                jobRequirementList = []
                jobBenefitList = []
                campaignNameList.append(campaign.name)
                campaignPositionList.append(campaign.position)
                jobs = campaign.campaign_jobs.all().filter(Q(is_active=True) & Q(end_time__gte=datetime.now()))
                for job in jobs:
                    jobTitleList.append(job.title)
                    jobDescriptionList.append(job.description)
                    jobRequirementList.append(job.job_requirement)
                    benefits = job.job_benefits.all()
                    for benefit in benefits:
                        jobBenefitList.append(benefit.benefit)
                print(jobTitleList)
                print(jobDescriptionList)
                # campaign search
                filterTitle_campaignName = reduce(operator.or_, (Q(title__icontains = item) for item in campaignNameList))
                filterTitle_campaignPosition = reduce(operator.or_, (Q(title__icontains = item) for item in campaignPositionList))
                filterTarget_campaignName = reduce(operator.or_, (Q(target_major__icontains = item) for item in campaignNameList))
                filterTarget_campaignPosition = reduce(operator.or_, (Q(target_major__icontains = item) for item in campaignPositionList))
                filterCvEducations_campaignName = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in campaignNameList))
                filterCvEducations_campaignPosition = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in campaignPositionList))
                filterCvExperiences_campaignName = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in campaignNameList))
                filterCvExperiences_campaignPosition = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in campaignPositionList))
                filterCvSkills_campaignName = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in campaignNameList))
                filterCvSkills_campaignPosition = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in campaignPositionList))
                filterSocialActivities_campaignName = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in campaignNameList))
                filterSocialActivities_campaignPosition = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in campaignPositionList))
                # searching jobs of campaign
                filterTitle_jobTitle = reduce(operator.or_, (Q(title__icontains = item) for item in jobTitleList))
                filterTitle_jobDescription = reduce(operator.or_, (Q(title__icontains = item) for item in jobDescriptionList))
                filterTitle_jobRequirement = reduce(operator.or_, (Q(title__icontains = item) for item in jobRequirementList))
                filterTarget_jobTitle = reduce(operator.or_, (Q(target_major__icontains = item) for item in jobTitleList))
                filterTarget_jobDescription = reduce(operator.or_, (Q(target_major__icontains = item) for item in jobDescriptionList))
                filterTarget_jobRequirement = reduce(operator.or_, (Q(target_major__icontains = item) for item in jobRequirementList))
                filterTarget_jobBenefit = reduce(operator.or_, (Q(target_major__icontains = item) for item in jobBenefitList))
                filterCvEducations_jobTitle = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in jobTitleList))
                filterCvEducations_jobDescription = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in jobDescriptionList))
                filterCvEducations_jobRequirement = reduce(operator.or_, (Q(cv_cv_educations__major__icontains = item) for item in jobRequirementList))
                filterCvExperiences_jobTitle = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in jobTitleList))
                filterCvExperiences_jobDescription = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in jobDescriptionList))
                filterCvExperiences_jobRequirement = reduce(operator.or_, (Q(cv_cv_experiences__job_title__icontains = item) for item in jobRequirementList))
                filterCvSkills_jobTitle = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in jobTitleList))
                filterCvSkills_jobDescription = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in jobDescriptionList))
                filterCvSkills_jobRequirement = reduce(operator.or_, (Q(cv_cv_skills__name__icontains = item) for item in jobRequirementList))
                filterSocialActivities_jobTitle = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in jobTitleList))
                filterSocialActivities_jobDescription = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in jobDescriptionList))
                filterSocialActivities_jobRequirement = reduce(operator.or_, (Q(cv_cv_social_activities__title__icontains = item) for item in jobRequirementList))
                # final
                queryset = queryset.filter(Q(filterTitle_campaignName) | Q(filterTarget_campaignName)
                                       | Q(filterTitle_campaignPosition) | Q(filterTarget_campaignPosition)
                                       | Q(filterCvEducations_campaignName) | Q(filterCvEducations_campaignPosition)
                                       | Q(filterCvExperiences_campaignName) | Q(filterCvExperiences_campaignPosition)
                                       | Q(filterCvSkills_campaignName) | Q(filterCvSkills_campaignPosition)
                                       | Q(filterSocialActivities_campaignName) | Q(filterSocialActivities_campaignPosition)
                                       | Q(filterTitle_jobTitle) | Q(filterTitle_jobDescription)
                                       | Q(filterTitle_jobRequirement) | Q(filterTarget_jobTitle)
                                       | Q(filterTarget_jobDescription) | Q(filterTarget_jobRequirement)
                                       | Q(filterTarget_jobBenefit) | Q(filterCvEducations_jobTitle)
                                       | Q(filterCvEducations_jobDescription) | Q(filterCvEducations_jobRequirement)
                                       | Q(filterCvExperiences_jobTitle) | Q(filterCvExperiences_jobTitle)
                                       | Q(filterCvExperiences_jobDescription) | Q(filterCvExperiences_jobRequirement)
                                       | Q(filterCvSkills_jobTitle) | Q(filterCvSkills_jobDescription)
                                       | Q(filterCvSkills_jobRequirement) | Q(filterSocialActivities_jobTitle)
                                       | Q(filterSocialActivities_jobDescription) | Q(filterSocialActivities_jobRequirement)).distinct()
                if queryset.count() == 0:
                    return Response({'message': 'Cv not found'}, status=status.HTTP_404_NOT_FOUND)
                # The ViewSet class inherits from APIView. The relation is: View(in Django) -> APIView -> ViewSet
                # The ModelViewSetclass inherits from GenericViewSet . The relation is: View(in Django) -> APIView -> GenericAPIView -> GenericViewSet -> ModelViewSet
                # pagination_class is add in GenericAPIView, so you can't use it in a class inherits from APIView.You can try viewsets.GenericViewSet.
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = CvSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = CvSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'cv': 'SaveCv not found'}, status=status.HTTP_404_NOT_FOUND)
        