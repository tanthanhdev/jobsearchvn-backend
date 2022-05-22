
# from django.conf.urls import url, include
from django.urls import path

from .views import *
# # Define class
analytic_user_list = AnalyticUserViewSet.as_view({
    'get': 'list', # Get lists
})

analytic_apply_list = AnalyticApplyViewSet.as_view({
    'get': 'list', # Get lists
})

urlpatterns = [
    # Unauthenticated
    path('analytic/users/', analytic_user_list, name='analytic_user_list'),
    path('analytic/applies/', analytic_apply_list, name='analytic_apply_list'),
]