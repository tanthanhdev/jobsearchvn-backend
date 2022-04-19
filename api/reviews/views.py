from django.shortcuts import render

# Create your views here.
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
from .serializers import ReviewSerializer, ReviewSerializer
from .serializers import _is_token_valid, get_user_token
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid, IsMember
from operator import or_, and_
from django.core import serializers

from api.users import status_http

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    default_serializer_classes = ReviewSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsMember]
    # permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Review.objects.filter(Q(employer__user=request.user))
            if queryset:
                serializer = ReviewSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'review': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'review': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, slug=None):
        try:
            queryset = Review.objects.get(slug=slug, employer__user=request.user)
            serializer = ReviewSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'review': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data, context={
            'request': request
        })
        messages = {}
        if serializer.is_valid():
            if not serializer.employer_exists():
                messages['Employer'] = "Employer not found"
            if messages:
                return Response(messages, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)                

# Review unauthenticated
class ReviewUnauthenticatedViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    default_serializer_classes = ReviewSerializer
    permission_classes = []
    pagination_class = None
    lookup_field = 'slug'
    # parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Review.objects.all()
            serializer = ReviewSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'review': 'Review not found'}, status=status.HTTP_400_BAD_REQUEST)


    
