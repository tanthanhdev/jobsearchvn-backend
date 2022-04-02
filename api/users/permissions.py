from rest_framework.permissions import BasePermission
from django.conf import settings


# Custom permission for users in token is exists.
class IsTokenValid(BasePermission):
    """
    Allows access only to user in token is exists.
    """
    message = {'message': 'Token is invalid or expired.'}
    
    def has_permission(self, request, view):
        return request.user and request.user.token is not None
    
class IsMember(BasePermission):
    """
    Allows access only to use in member roles.
    """
    message = {'message': 'You are not a member.'}
    
    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_staff is not True
    
class IsEmployer(BasePermission):
    """
    Allows access only to use in employer roles.
    """
    message = {'message': 'You are not a employer.'}
    
    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_staff