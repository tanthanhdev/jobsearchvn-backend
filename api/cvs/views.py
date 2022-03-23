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
from .serializers import CvSerializer, CvUpdateSerializer, Cv_TemplateSerializer, Cv_CareerSerializer, Cv_DesignSerializer
from .serializers import _is_token_valid, get_user_token
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid
from operator import or_, and_
from django.core import serializers

from api.users import status_http

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
                return Response(messages, status=status.HTTP_204_NO_CONTENT)
            print('vao roi ma?????????????????????????????????????????')
            print(request.data)
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
                    return Response(messages, status=status.HTTP_204_NO_CONTENT)
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
                    return Response({'cv': 'Cv Not Found'}, status=status.HTTP_204_NO_CONTENT)
                queryset.delete()
                return Response({'message': 'Delete all cv successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                queryset = Cv.objects.get(Q(slug=slug), Q(user=request.user), Q(user__is_active=True))
                queryset.delete()
                return Response({'message': 'Delete cv successfully'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'cv_template': 'Cv_Template not found'}, status=status.HTTP_204_NO_CONTENT)
    
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
                return Response({'cv_template': 'Cv_Template not found'}, status=status.HTTP_204_NO_CONTENT)
        
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
            return Response({'cv_career': 'Cv_Career not found'}, status=status.HTTP_204_NO_CONTENT)
        
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
            return Response({'cv_design': 'Cv_Design not found'}, status=status.HTTP_204_NO_CONTENT)
