from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from s3direct.fields import S3DirectField
from django.db import transaction
import uuid
from django.utils.text import slugify 
from django.utils.crypto import get_random_string
from django.core.validators import validate_image_file_extension
from django.db.models.signals import post_save
from django.dispatch import receiver
# Models
from api.employers.models import Employer
from api.members.models import Member

# Create your models here.
CURRENCY_CHOICES =(
  ("VND", "vnd"),
  ("USD", "dollar"),
)

LOCATION_CHOICES =(
  ("Tất Cả Địa Điểm", "tat ca dia diem"),
  ("Đà Nẵng", "da nang"),
  ("Hà Nội", "ha noi"),
  ("Tp. Hồ Chí Minh", "ho chi minh"),
  ("Quảng Nam", "quang nam"),
)

def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug

# Table Reviews
class Review(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="employer_reviews")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_reviews")
    #
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    point = models.FloatField(null=True, blank=True)
    status = models.BooleanField(default=True, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'reviews'
    
    def __str__(self):
        return self.title
    