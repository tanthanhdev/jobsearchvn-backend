
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

urlpatterns = [
    # url('cvs/<slug:slug>/', cv_detail, name='cvs_detail'),
    url('cvs/', cv_list, name='cv_list'),
    # cv template model
    path('public/cv-template/', cv_template_unauth_list, name='cv_template_unauth_list'),
    path('public/view/cv-template/', view_public_cv_template, name='view_public_cv_template'),
    # cv_careers
    path('public/cv_careers/', cv_career_unauth_list, name='cv_career_unauth_list'),
    # cv_design
    path('public/cv_designs/', cv_design_unauth_list, name='cv_design_unauth_list'),
]