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
from datetime import datetime    

from api.members.models import Apply, RegisterNotification
from api.members.serializers import ApplySerializer
from .models import *
from .serializers import (
    JobSerializer, JobUpdateSerializer, TagSerializer,
    CountrySerializer, CitySerializer, CampaignSerializer,
    CampaignUpdateSerializer, JobTypeSerializer,
    SwitchActiveJobSerializer, CronJobJobSerializer)
from .serializers import _is_token_valid, get_user_token
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid, IsEmployer
from operator import or_, and_
from django.core import serializers

from api.users.custom_pagination import CustomPagination
from api.users import status_http
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    default_serializer_classes = JobSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Job.objects.filter(Q(employer__user=request.user))
            if queryset:
                serializer = JobSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'message': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Job.objects.get(slug=slug, employer__user=request.user)
            serializer = JobSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = JobSerializer(data=request.data, context={
            'request': request
        })
        messages = {}
        if serializer.is_valid():
            if not serializer.job_type_exists():
                messages['Job type'] = "Job type not found"
            if not serializer.country_exists():
                messages['Country'] = "Country not found"
            if not serializer.campaign_exists():
                messages['Campaign'] = "Campaign not found"
            if messages:
                return Response(messages, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)                

    def update(self, request, slug, format=None):
        try:
            queryset = Job.objects.get(Q(slug=slug), Q(employer__user=request.user))
        except:
            return Response({'message': 'Job Update Not Found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = JobUpdateSerializer(queryset, data=data, context={
            'request': request
        })
        messages = {}
        if serializer.is_valid():
            if not serializer.job_type_exists():
                messages['Job type'] = "Job type not found"
            if not serializer.country_exists():
                messages['Country'] = "Country not found"
            if messages:
                return Response(messages, status=status.HTTP_400_BAD_REQUEST)
            serializer.tag_new()
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, slug=None, format=None):
        try:
            if not slug:
                queryset = Job.objects.filter(empployer=request.user.employer)
                if not queryset:
                    return Response({'job': 'Job Not Found'}, status=status.HTTP_400_BAD_REQUEST)
                queryset.delete()
                return Response({'message': 'Delete all job successfully'}, status=status.HTTP_200_OK)
            else:
                queryset = Job.objects.get(Q(slug=slug) & Q(employer=request.user.employer))
                queryset.delete()
                return Response({'message': 'Delete job successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class SwitchActiveJobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    default_serializer_classes = SwitchActiveJobSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)

    def update(self, request, slug, format=None):
        queryset = None
        try:
            queryset = Job.objects.get(Q(slug=slug), Q(employer__user=request.user))
            data = request.data
            serializer = SwitchActiveJobSerializer(queryset, data=data, context={
                'request': request
            })
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Job Update Not Found'}, status=status.HTTP_404_NOT_FOUND)

# Campaigns
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    default_serializer_classes = CampaignSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Campaign.objects.filter(employer__user=request.user)
            if request.GET:
                query_string = request.GET.get('q').strip()
                if query_string:
                    if query_string:
                        queryset = queryset.filter(Q(name__icontains=query_string) | Q(position__icontains=query_string))
                    if queryset.count() == 0:
                        return Response({'message': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)
                    serializer = CampaignSerializer(queryset, many=True)
            serializer = CampaignSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Campaign.objects.get(slug=slug, employer__user=request.user)
            serializer = CampaignSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = CampaignSerializer(data=request.data, context={
            'request': request
        })
        messages = {}
        if serializer.is_valid():
            if not serializer.city_exists():
                messages['city'] = "City not found"
            if messages:
                return Response(messages, status=status.HTTP_404_NOT_FOUND)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)                

    def update(self, request, slug, format=None):
        queryset = None
        try:
            queryset = Campaign.objects.get(slug=slug, employer__user=request.user)
            data = request.data
            serializer = CampaignUpdateSerializer(queryset, data=data, context={
                'request': request
            })
            messages = {}
            if serializer.is_valid():
                if not serializer.city_exists():
                    messages['city'] = "City not found"
                if messages:
                    return Response(messages, status=status.HTTP_404_NOT_FOUND)
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Campaign update Not Found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, slug=None, format=None):
        try:
            if not slug:
                queryset = Campaign.objects.filter(employer__user=request.user)
                if not queryset:
                    return Response({'message': 'Campaign Not Found'}, status=status.HTTP_400_BAD_REQUEST)
                queryset.delete()
                return Response({'message': 'Delete all campaign successfully'}, status=status.HTTP_200_OK)
            else:
                queryset = Campaign.objects.get(slug=slug)
                queryset.delete()
                return Response({'message': 'Delete campaign successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
# CV apply for campaign
class ApplyCampaignViewSet(viewsets.ModelViewSet):
    queryset = Apply.objects.all()
    default_serializer_classes = ApplySerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def retrieve(self, request, slug=None):
        try:
            campaign = Campaign.objects.get(slug=slug)
            queryset = Apply.objects.filter(job__campaign=campaign)
            serializer = ApplySerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Apply not found'}, status=status.HTTP_404_NOT_FOUND)

class JobCampaignViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    default_serializer_classes = JobSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = CustomPagination
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, slug=None , *args, **kwargs):
        try:
            queryset = Job.objects.filter(Q(campaign__slug=slug), Q(employer=request.user.employer))
            if queryset:
                serializer = JobSerializer(queryset, many=True)
                # pagination here
                # The ViewSet class inherits from APIView. The relation is: View(in Django) -> APIView -> ViewSet
                # The ModelViewSetclass inherits from GenericViewSet . The relation is: View(in Django) -> APIView -> GenericAPIView -> GenericViewSet -> ModelViewSet
                # pagination_class is add in GenericAPIView, so you can't use it in a class inherits from APIView.You can try viewsets.GenericViewSet.
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = JobSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = JobSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'message': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

# Job unauthenticated
class JobUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    default_serializer_classes = JobSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Job.objects.filter(Q(is_active=True), Q(end_time__gte=datetime.now())) #Greater than or equal
            if queryset:
                serializer = JobSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'job': 'Job not found'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'job': 'Job not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Job.objects.get(slug=slug, is_active=True)
            serializer = JobSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'job': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        
# Tag unauthenticated
class TagUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    default_serializer_classes = TagSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Tag.objects.all()
            serializer = TagSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'tag': 'Tag not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Tag.objects.get(slug=slug)
            serializer = TagSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'tag': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        serializer = TagSerializer(data=request.data)
        messages = {}
        if serializer.is_valid():
            if serializer.tag_name_exists():
                messages['name'] = "Tag name exists"
            if messages:
                return Response(messages, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)                

    def destroy(self, request, slug=None, format=None):
        try:
            if slug:
                queryset = Tag.objects.get(slug=slug)
                queryset.delete()
                return Response({'message': 'Delete tag successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
        
        
# Country unauthenticated
class CountryUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    default_serializer_classes = CountrySerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Country.objects.all()
            serializer = CountrySerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'country': 'Country not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Country.objects.get(slug=slug)
            serializer = CountrySerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'country': 'Country not found'}, status=status.HTTP_404_NOT_FOUND)

        
# City unauthenticated
class CityUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    default_serializer_classes = CitySerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = City.objects.all()
            serializer = CitySerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'city': 'City not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = City.objects.get(slug=slug)
            serializer = CitySerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'city': 'City not found'}, status=status.HTTP_404_NOT_FOUND)
        
# JobType unauthenticated
class JobTypeUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = JobType.objects.all()
    default_serializer_classes = JobTypeSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = JobType.objects.all()
            serializer = JobTypeSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'JobType not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = JobType.objects.get(slug=slug)
            serializer = JobTypeSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'JobType not found'}, status=status.HTTP_404_NOT_FOUND)

# Cronjobs jobs (unauthorized)
class CronJobJobsViewSet(viewsets.ModelViewSet):
    queryset = RegisterNotification.objects.all()
    default_serializer_classes = CronJobJobSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            registerNotifications = RegisterNotification.objects.filter(status=True, cron_job=request.GET.get('cron_job', ''))
            for item in registerNotifications:
                jobs = Job.objects.filter(Q(title__icontains=item.job_name), Q(level=item.level)
                                         | Q(job_job_addresses__address__icontains=item.district)
                                         , Q(job_type__name__icontains=item.major)
                                         , Q(salary__gt=item.salary), Q(currency=item.currency)).order_by('-pk')[:3]
                # send mail
                try:
                    message = render_to_string(
                        'api/mail/template_jobs.html', {'jobs': jobs})
                except Exception as e:
                    print(e)
                send = EmailMessage('Bạn đang có một số công việc phù hợp từ JobSearchVN!', message,
                                    from_email=settings.EMAIL_FROM, to=[item.member.user.email])
                send.content_subtype = 'html'
                send.send()
                # update mail sent all of them
                for job in jobs:
                    job.is_mail_sent = True
                    job.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Cronjob not working'}, status=status.HTTP_400_BAD_REQUEST)
        