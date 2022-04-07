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
from .serializers import FollowSerializer, MemberSerializer, MemberUpdateSerializer, SaveJobSerializer
from .serializers import _is_token_valid, get_user_token
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
import json
from django.core.serializers.json import DjangoJSONEncoder
from api.users.permissions import IsTokenValid, IsMember
from operator import or_, and_
# custom
from api.users.custom_pagination import CustomPagination

from api.users import status_http

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    default_serializer_classes = MemberSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsMember]
    # permission_classes = []
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def retrieve(self, request):
        try:
            queryset = Member.objects.get(user=request.user)
            serializer = MemberSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'member': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, format=None):
        try:
            queryset = Member.objects.get(user=request.user)
            data = request.data
            serializer = MemberUpdateSerializer(queryset, data=data, context={
                'request': request
            })
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Member Update Not Found'}, status=status.HTTP_404_NOT_FOUND)

class FollowCompanyViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    default_serializer_classes = FollowSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsMember]
    # permission_classes = []
    pagination_class = None
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Follow.objects.filter(Q(member__user=request.user))
            if queryset:
                serializer = FollowSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'follow': 'Follow not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'follow': 'Follow not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, id=None):
        try:
            queryset = Follow.objects.get(member__user=request.user, member_id=id)
            serializer = FollowSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'follow': 'Follow not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = FollowSerializer(data=request.data, context={
            'request': request
        })
        messages = {}
        if serializer.is_valid():
            if serializer.follow_exists():
                messages['Follow'] = "Follow has exists"
            if not serializer.member_exists():
                messages['Member'] = "Member not found"
            if messages:
                return Response(messages, status=status.HTTP_204_NO_CONTENT)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, id=None, format=None):
        try:
            if not id:
                queryset = Follow.objects.filter(member__user=request.user)
                if not queryset:
                    return Response({'follow': 'Follow Not Found'}, status=status.HTTP_204_NO_CONTENT)
                queryset.delete()
                return Response({'message': 'Delete all follow successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                queryset = Follow.objects.get(Q(member_id=id), Q(member__user=request.user))
                queryset.delete()
                return Response({'message': 'Delete follow successfully'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
        
class SaveJobViewSet(viewsets.ModelViewSet):
    queryset = SaveJob.objects.all()
    default_serializer_classes = SaveJobSerializer
    permission_classes = [IsAuthenticated, IsTokenValid, IsMember]
    # permission_classes = []
    pagination_class = None
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_classes)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = SaveJob.objects.filter(Q(member__user=request.user))
            if queryset:
                serializer = SaveJobSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'save job': 'SaveJob not found'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'save job': 'SaveJob not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, id=None):
        try:
            queryset = SaveJob.objects.get(member__user=request.user, member_id=id)
            serializer = SaveJobSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'save job': 'SaveJob not found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = SaveJobSerializer(data=request.data, context={
            'request': request
        })
        messages = {}
        if serializer.is_valid():
            if serializer.save_jobs_exists():
                messages['SaveJob'] = "SaveJob has exists"
            if not serializer.job_exists():
                messages['Job'] = "Job not found"
            if messages:
                return Response(messages, status=status.HTTP_204_NO_CONTENT)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, id=None, format=None):
        try:
            if not id:
                queryset = SaveJob.objects.filter(member__user=request.user)
                if not queryset:
                    return Response({'save job': 'SaveJob Not Found'}, status=status.HTTP_204_NO_CONTENT)
                queryset.delete()
                return Response({'message': 'Delete all save job successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                queryset = Follow.objects.get(Q(member_id=id), Q(member__user=request.user))
                queryset.delete()
                return Response({'message': 'Delete save job successfully'}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)