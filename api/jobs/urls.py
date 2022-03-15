
from django.conf.urls import url, include
from django.urls import path

from rest_framework import permissions

from .views import *
                        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# # Define class

job_detail = JobViewSet.as_view({
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    'delete': 'destroy', # delete
})

job_list = JobViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create' # Create a new
})

job_unauth_list = JobUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})

job_unauth_detail = JobUnauthenticatedViewSet.as_view({
    'get': 'retrieve', # get detail
})

# Tags model
tag_unauth_list = TagUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create', # Create a new
})

tag_unauth_detail = TagUnauthenticatedViewSet.as_view({
    'get': 'retrieve', # get detail
    'delete': 'destroy', # delete
})

urlpatterns = [
    # dashboard
    path('jobs/<slug:slug>/', job_detail, name='job_detail'),
    path('jobs/', job_list, name='job_list'),
    # Unauthenticated
    path('public/jobs/<slug:slug>/', job_unauth_detail, name='job_unauth_detail'),
    path('public/jobs/', job_unauth_list, name='job_unauth_list'),
    # Tags model
    path('public/tags/<slug:slug>/', tag_unauth_detail, name='tag_unauth_detail'),
    path('public/tags/', tag_unauth_list, name='tag_unauth_list'),
]