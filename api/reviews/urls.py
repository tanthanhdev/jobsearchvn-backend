
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

review_detail = ReviewViewSet.as_view({
    'get': 'retrieve', # get detail
})

review_list = ReviewViewSet.as_view({
    'get': 'list', # Get lists
    'post': 'create' # Create a new
})

review_unauth_list = ReviewUnauthenticatedViewSet.as_view({
    'get': 'list', # Get lists
})


urlpatterns = [
    # dashboard
    path('reviews/<slug:slug>/', review_detail, name='review_detail'),
    path('reviews/', review_list, name='review_list'),
    # Unauthenticated
    path('public/reviews/', review_unauth_list, name='review_unauth_list'),
]