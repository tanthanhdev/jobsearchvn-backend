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
from .serializers import EmployerSerializer, EmployerUpdateSerializer, PublicEmployerSerializer
from .serializers import _is_token_valid, get_user_token
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid, IsEmployer
from operator import or_, and_
# custom
from api.users.custom_pagination import CustomPagination

from api.users import status_http

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    default_serializer_classes = EmployerSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsEmployer]
    # permission_classes = []
    pagination_class = None
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def retrieve(self, request):
        try:
            queryset = Employer.objects.get(user=request.user)
            serializer = EmployerSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'employer': 'Employer not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, format=None):
        try:
            queryset = Employer.objects.get(user=request.user)
            data = request.data
            serializer = EmployerUpdateSerializer(queryset, data=data, context={
                'request': request
            })
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'message': 'Employer Update Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
# Public employer
class PublicEmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.filter(user__is_active=True, user__is_staff=True)
    default_serializer_classes = PublicEmployerSerializer
    permission_classes = []
    pagination_class = CustomPagination
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            # The ViewSet class inherits from APIView. The relation is: View(in Django) -> APIView -> ViewSet
            # The ModelViewSetclass inherits from GenericViewSet . The relation is: View(in Django) -> APIView -> GenericAPIView -> GenericViewSet -> ModelViewSet
            # pagination_class is add in GenericAPIView, so you can't use it in a class inherits from APIView.You can try viewsets.GenericViewSet.
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = PublicEmployerSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = PublicEmployerSerializer(self.queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'employer': 'Employer not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Employer.objects.get(slug=slug, user__is_active=True, user__is_staff=True)
            serializer = PublicEmployerSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'employer': 'Employer not found'}, status=status.HTTP_404_NOT_FOUND)