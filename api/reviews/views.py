# from django.shortcuts import render

# # Create your views here.
# from functools import reduce
# from django.utils.timezone import now
# from django.shortcuts import render, redirect, get_object_or_404
# from django.conf import settings
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, permission_classes, action
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.parsers import MultiPartParser, FormParser
# from django.contrib.auth.models import User, Group, Permission
# from rest_framework import viewsets
# from rest_framework import status
# from django.db.models import Q, query
# from collections import OrderedDict
# from rest_framework_simplejwt.tokens import RefreshToken

# from .models import *
# from .serializers import JobSerializer, JobUpdateSerializer, TagSerializer, CountrySerializer, CitySerializer
# from .serializers import _is_token_valid, get_user_token
# from django.contrib.auth import logout
# from django.core.exceptions import ObjectDoesNotExist
# import json
# from django.core.serializers.json import DjangoJSONEncoder
# from api.users.permissions import IsTokenValid
# from operator import or_, and_
# from django.core import serializers

# from api.users import status_http

# class JobViewSet(viewsets.ModelViewSet):
#     queryset = Job.objects.all()
#     default_serializer_classes = JobSerializer
#     permission_classes = [IsAuthenticated, IsTokenValid]
#     # permission_classes = []
#     pagination_class = None
#     lookup_field = 'slug'
#     # parser_classes = [MultiPartParser, FormParser]
    
#     def get_serializer_class(self):
#         return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = Job.objects.filter(Q(employer__user=request.user))
#             if queryset:
#                 serializer = JobSerializer(queryset, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response({'job': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
#         except:
#             return Response({'job': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
#     def retrieve(self, request, slug=None):
#         try:
#             queryset = Job.objects.get(slug=slug, employer__user=request.user)
#             serializer = JobSerializer(queryset)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except:
#             return Response({'job': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

#     def create(self, request, *args, **kwargs):
#         serializer = JobSerializer(data=request.data, context={
#             'request': request
#         })
#         messages = {}
#         if serializer.is_valid():
#             if not serializer.job_type_exists():
#                 messages['Job type'] = "Job type not found"
#             if not serializer.country_exists():
#                 messages['Country'] = "Country not found"
#             if messages:
#                 return Response(messages, status=status.HTTP_204_NO_CONTENT)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)                

#     def update(self, request, slug, format=None):
#         queryset = None
#         try:
#             queryset = Job.objects.get(Q(slug=slug), Q(employer__user=request.user))
#             data = request.data
#             serializer = JobUpdateSerializer(queryset, data=data, context={
#                 'request': request
#             })
#             messages = {}
#             if serializer.is_valid():
#                 if not serializer.job_type_exists():
#                     messages['Job type'] = "Job type not found"
#                 if not serializer.country_exists():
#                     messages['Country'] = "Country not found"
#                 if messages:
#                     return Response(messages, status=status.HTTP_204_NO_CONTENT)
#                 serializer.tag_new()
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response({'message': 'Job Update Not Found'}, status=status.HTTP_404_NOT_FOUND)

#     def destroy(self, request, slug=None, format=None):
#         try:
#             if not slug:
#                 queryset = Job.objects.filter(empployer__user=request.user)
#                 if not queryset:
#                     return Response({'job': 'Job Not Found'}, status=status.HTTP_204_NO_CONTENT)
#                 queryset.delete()
#                 return Response({'message': 'Delete all job successfully'}, status=status.HTTP_204_NO_CONTENT)
#             else:
#                 queryset = Job.objects.get(Q(slug=slug), Q(employer__user=request.user))
#                 queryset.delete()
#                 return Response({'message': 'Delete job successfully'}, status=status.HTTP_204_NO_CONTENT)
#         except:
#             return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
    
# # Job unauthenticated
# class JobUnauthenticatedViewSet(viewsets.ModelViewSet):
#     queryset = Job.objects.all()
#     default_serializer_classes = JobSerializer
#     permission_classes = []
#     pagination_class = None
#     lookup_field = 'slug'
#     # parser_classes = [MultiPartParser, FormParser]
    
#     def get_serializer_class(self):
#         return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = Job.objects.all()
#             if queryset:
#                 serializer = JobSerializer(queryset, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response({'job': 'Job not found'}, status=status.HTTP_204_NO_CONTENT)
#         except:
#             return Response({'job': 'Job not found'}, status=status.HTTP_204_NO_CONTENT)
    
#     def retrieve(self, request, slug=None):
#         try:
#             queryset = Job.objects.get(slug=slug)
#             serializer = JobSerializer(queryset)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except:
#             return Response({'job': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        
# # Tag unauthenticated
# class TagUnauthenticatedViewSet(viewsets.ModelViewSet):
#     queryset = Tag.objects.all()
#     default_serializer_classes = TagSerializer
#     permission_classes = []
#     pagination_class = None
#     lookup_field = 'slug'
#     # parser_classes = [MultiPartParser, FormParser]
    
#     def get_serializer_class(self):
#         return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = Tag.objects.all()
#             serializer = TagSerializer(queryset, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except:
#             return Response({'tag': 'Tag not found'}, status=status.HTTP_204_NO_CONTENT)
    
#     def retrieve(self, request, slug=None):
#         try:
#             queryset = Tag.objects.get(slug=slug)
#             serializer = TagSerializer(queryset)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except:
#             return Response({'tag': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
    
#     def create(self, request, *args, **kwargs):
#         serializer = TagSerializer(data=request.data)
#         messages = {}
#         if serializer.is_valid():
#             if serializer.tag_name_exists():
#                 messages['name'] = "Tag name exists"
#             if messages:
#                 return Response(messages, status=status.HTTP_204_NO_CONTENT)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)                

#     def destroy(self, request, slug=None, format=None):
#         try:
#             if slug:
#                 queryset = Tag.objects.get(slug=slug)
#                 queryset.delete()
#                 return Response({'message': 'Delete tag successfully'}, status=status.HTTP_204_NO_CONTENT)
#         except:
#             return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
        
        
# # Country unauthenticated
# class CountryUnauthenticatedViewSet(viewsets.ModelViewSet):
#     queryset = Country.objects.all()
#     default_serializer_classes = CountrySerializer
#     permission_classes = []
#     pagination_class = None
#     lookup_field = 'slug'
#     # parser_classes = [MultiPartParser, FormParser]
    
#     def get_serializer_class(self):
#         return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = Country.objects.all()
#             serializer = CountrySerializer(queryset, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except:
#             return Response({'country': 'Country not found'}, status=status.HTTP_204_NO_CONTENT)
    
#     def retrieve(self, request, slug=None):
#         try:
#             queryset = Country.objects.get(slug=slug)
#             serializer = CountrySerializer(queryset)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except:
#             return Response({'country': 'Country not found'}, status=status.HTTP_404_NOT_FOUND)

        
# # City unauthenticated
# class CityUnauthenticatedViewSet(viewsets.ModelViewSet):
#     queryset = City.objects.all()
#     default_serializer_classes = CitySerializer
#     permission_classes = []
#     pagination_class = None
#     lookup_field = 'slug'
#     # parser_classes = [MultiPartParser, FormParser]
    
#     def get_serializer_class(self):
#         return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = City.objects.all()
#             serializer = CitySerializer(queryset, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except:
#             return Response({'city': 'City not found'}, status=status.HTTP_204_NO_CONTENT)
    
#     def retrieve(self, request, slug=None):
#         try:
#             queryset = City.objects.get(slug=slug)
#             serializer = CitySerializer(queryset)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except:
#             return Response({'city': 'City not found'}, status=status.HTTP_404_NOT_FOUND)

    
