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

from .models import *
from api.jobs.models import Job
from api.cvs.models import Cv
from api.jobs.serializers import JobSerializer
from api.cvs.serializers import CvSerializer
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid
from operator import or_, and_

from api.users import status_http

from api.users.custom_pagination import CustomPagination
from datetime import datetime    

class SearchJobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(Q(is_active=True), Q(end_time__gte=datetime.now()))
    default_serializer_classes = JobSerializer
    permission_classes = []
    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_string = request.GET.get('q')
        address = request.GET.get('adr')
        # filter here
        if query_string:
            query_string = query_string.strip()
            queryset = queryset.filter(Q(title__icontains=query_string) | Q(employer__company_name__icontains=query_string)
                                          | Q(employer__company_location__icontains=query_string) 
                                          | Q(description__icontains=query_string)
                                          | Q(job_job_addresses__address__icontains=query_string))
        if address:
            address = address.strip()
            queryset = queryset.filter(Q(job_job_addresses__city__name__icontains=address))
        if queryset.count() == 0:
            return Response({'message': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
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
    
class SearchCvViewSet(viewsets.ModelViewSet):
    queryset = Cv.objects.filter(status=1)
    default_serializer_classes = CvSerializer
    permission_classes = []
    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_string = request.GET.get('q')
        # filter here
        if query_string:
            query_string = query_string.strip()
            queryset = queryset.filter(Q(title__icontains=query_string)
                                          | Q(target_major__icontains=query_string))
        if queryset.count() == 0:
            return Response({'message': 'Cv not found'}, status=status.HTTP_404_NOT_FOUND)
        # pagination here
        # The ViewSet class inherits from APIView. The relation is: View(in Django) -> APIView -> ViewSet
        # The ModelViewSetclass inherits from GenericViewSet . The relation is: View(in Django) -> APIView -> GenericAPIView -> GenericViewSet -> ModelViewSet
        # pagination_class is add in GenericAPIView, so you can't use it in a class inherits from APIView.You can try viewsets.GenericViewSet.
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CvSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CvSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)