
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
switch_active_job_detail = SwitchActiveJobViewSet.as_view({
    'patch': 'update', # get detail
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

# Countries model
country_unauth_list = CountryUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})

country_unauth_detail = CountryUnauthenticatedViewSet.as_view({
    'get': 'retrieve', # get detail
})
# city
city_unauth_list = CityUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})

city_unauth_detail = CityUnauthenticatedViewSet.as_view({
    'get': 'retrieve', # get detail
})
# Campaigns
campaign_detail = CampaignViewSet.as_view({
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    'delete': 'destroy', # delete
})

campaign_list = CampaignViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create', # Create a new
    'delete': 'destroy', # delete all
})

job_campaign_detail = JobCampaignViewSet.as_view({
    'get': 'list', # get detail
})
# job types
job_types_unauth_list = JobTypeUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})

job_types_unauth_detail = JobTypeUnauthenticatedViewSet.as_view({
    'get': 'retrieve', # get detail
})
# Cv apply campaign
apply_campaign_detail = ApplyCampaignViewSet.as_view({
    'get': 'retrieve', # get detail
})

urlpatterns = [
    # dashboard
    path('jobs/<slug:slug>/', job_detail, name='job_detail'),
    path('jobs/', job_list, name='job_list'),
    path('switch-active/job/<slug:slug>/', switch_active_job_detail, name='switch_active_job_detail'),
    # Unauthenticated
    path('public/jobs/<slug:slug>/', job_unauth_detail, name='job_unauth_detail'),
    path('public/jobs/', job_unauth_list, name='job_unauth_list'),
    # Tags model
    path('public/tags/<slug:slug>/', tag_unauth_detail, name='tag_unauth_detail'),
    path('public/tags/', tag_unauth_list, name='tag_unauth_list'),
    # Countries model
    path('public/countries/<slug:slug>/', country_unauth_detail, name='country_unauth_detail'),
    path('public/countries/', country_unauth_list, name='country_unauth_list'),
    # Cities model
    path('public/cities/<slug:slug>/', city_unauth_detail, name='city_unauth_detail'),
    path('public/cities/', city_unauth_list, name='city_unauth_list'),
    # Campaigns
    path('campaigns/<slug:slug>/', campaign_detail, name='campaign_detail'),
    path('campaigns/', campaign_list, name='campaign_list'),
    path('jobs/campaign/<slug:slug>/', job_campaign_detail, name='job_campaign_detail'),
    # Public job types
    path('public/job-types/<slug:slug>/', job_types_unauth_detail, name='job_types_unauth_detail'),
    path('public/job-types/', job_types_unauth_list, name='job_types_unauth_list'),
    # Cv apply for campaign
    path('apply/campaigns/<slug:slug>/', apply_campaign_detail, name='apply_campaign_detail'),
]