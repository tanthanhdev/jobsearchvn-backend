
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

cv_detail = CvViewSet.as_view({
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    'delete': 'destroy', # delete
})

cv_list = CvViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create', # Create a new
    'delete': 'destroy', # delete all
})
# cv template
cv_template_unauth_list = Cv_TemplateUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
    'patch': 'update', # update
})

view_public_cv_template = ViewPublicCv_TemplateViewSet.as_view({
    'post': 'setView', # get detail
})
# cv_career
cv_career_unauth_list = Cv_CareerUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})
# cv_design
cv_design_unauth_list = Cv_DesignUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})
# cv save
cv_save_detail = CvSaveViewSet.as_view({
    'get': 'retrieve', # get detail
    # 'patch': 'update', # update
    'delete': 'destroy', # delete
})
cv_save_list = CvSaveViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create', # Create a new
    'delete': 'destroy', # delete all
})
# match cv
match_cv_list = MatchCVViewSet.as_view({
    'get': 'list', # Get lists
})
match_cv_of_campaign_list = MatchCVCampaignViewSet.as_view({
    'get': 'list', # Get lists
})

urlpatterns = [
    path('cvs/save/<int:id>/', cv_save_detail, name='cv_save_detail'),
    path('cvs/save/', cv_save_list, name='cv_save_list'),
    path('cvs/<slug:slug>/', cv_detail, name='cvs_detail'),
    path('cvs/', cv_list, name='cv_list'),
    # cv template model
    path('public/cv-template/', cv_template_unauth_list, name='cv_template_unauth_list'),
    path('public/view/cv-template/', view_public_cv_template, name='view_public_cv_template'),
    # cv_careers
    path('public/cv_careers/', cv_career_unauth_list, name='cv_career_unauth_list'),
    # cv_design
    path('public/cv_designs/', cv_design_unauth_list, name='cv_design_unauth_list'),
    # match cv* (special)
    path('match-cv/', match_cv_list , name='match_cv_list'),
    path('match-cv/campaign/<int:id>/', match_cv_of_campaign_list , name='match_cv_of_campaign_list'),
]