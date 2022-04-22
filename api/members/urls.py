
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
# member_list = MemberViewSet.as_view({
#     # 'get': 'list', # Get lists
#     # 'post': 'create' # Create a new
# })

member_detail = MemberViewSet.as_view({
    'get': 'retrieve', # get detail
    'patch': 'update', # update
    # 'delete': 'destroy', # delete
})
# follow companies
follow_list = FollowCompanyViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create', # Create a new
    'delete': 'destroy', # delete all
})

follow_detail = FollowCompanyViewSet.as_view({
    'get': 'retrieve', # get detail
    # 'patch': 'update', # update
    'delete': 'destroy', # delete
})
# save jobs
save_job_list = SaveJobViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create', # Create a new
    'delete': 'destroy', # delete all
})

save_job_detail = SaveJobViewSet.as_view({
    'get': 'retrieve', # get detail
    # 'patch': 'update', # update
    'delete': 'destroy', # delete
})
# apply jobs
apply_job_list = ApplyJobViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create', # Create a new
    'delete': 'destroy', # delete all
})

apply_job_detail = ApplyJobViewSet.as_view({
    'get': 'retrieve', # get detail
    # 'patch': 'update', # update
    'delete': 'destroy', # delete
})

apply_job_for_employer_detail = ApplyJobForEmployerViewSet.as_view({
    'patch': 'update', # update
})

urlpatterns = [
    # # dashboard
    # path('members', member_list),
    path('members/', member_detail, name='member_detail'),
    # follow companies
    path('follow/companies/', follow_list, name='follow_list'),
    path('follow/companies/<int:id>/', follow_detail, name='follow_detail'),
    # save jobs
    path('save/jobs/', save_job_list, name='save_job_list'),
    path('save/jobs/<int:id>/', save_job_detail, name='save_job_detail'),
    # apply jobs
    path('apply/jobs/', apply_job_list, name='apply_job_list'),
    path('apply/jobs/<int:id>/', apply_job_detail, name='apply_job_detail'),
    path('employer/apply/jobs/<int:id>/', apply_job_for_employer_detail, name='apply_job_for_employer_detail'),
]