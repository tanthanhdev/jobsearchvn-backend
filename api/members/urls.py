
from django.conf.urls import url, include
from django.urls import path

from rest_framework import permissions

from .views import *
                        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# # # Define class
# tag_list = TagViewSet.as_view({
#     'get': 'list', # Get lists
#     'post': 'create' # Create a new
# })

# tag_detail = TagViewSet.as_view({
#     'get': 'retrieve', # get detail
#     # 'patch': 'update', # update
#     # 'delete': 'destroy', # delete
# })
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

urlpatterns = [
    # # dashboard
    # path('tags', tag_list),
    # # path('tags/delete-all', tag_detail, name='tag_delete_all'),
    # path('tags/<slug:slug>', tag_detail, name='tag_detail'),
    # follow companies
    path('follow/companies/', follow_list, name='follow_list'),
    path('follow/companies/<int:id>/', follow_detail, name='follow_detail'),
]