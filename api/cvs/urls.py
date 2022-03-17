
from django.conf.urls import url, include
from django.urls import path

from rest_framework import permissions

from .views import *
                        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# Define class

# cv_detail = CvViewSet.as_view({
#     'get': 'retrieve', # get detail
#     'patch': 'update', # update
#     'delete': 'destroy', # delete
# })

cv_list = CvViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create', # Create a new
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    'delete': 'destroy', # delete
})

urlpatterns = [
    # url('cvs/<slug:slug>/', cv_detail, name='cvs_detail'),
    url('cvs/', cv_list, name='cv_list'),
]