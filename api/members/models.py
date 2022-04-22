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
from api.users.models import User
from api.employers.models import Employer
from api.jobs.models import Job

# Create your models here.
def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug

# Table Members
def member_upload_file(instance,filename):
    id = str(instance).split('-')[0]
    return "member/{id}/avatars/{filename}".format(filename=filename, id=id)
    # return "account/employer/images/{random}_{filename}".format(filename=filename, random=get_random_string(4)) 

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    avatar = models.ImageField(upload_to=member_upload_file, null=True, blank=True)
    resume = models.CharField(max_length=255, null=True, blank=True)
    salary = models.BigIntegerField(blank=True, null=True)
    is_looking_for_a_job = models.BooleanField(blank=True, null=True, default=False)
    currency = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-user',)
        db_table = 'members'
    
    def __str__(self):
        return self.user.email
    
    def member_user_email(self):
        try:
            return self.user.email
        except:
            return None
        
    def delete(self, using=None, keep_parents=False):
        # try:
        #     self.image.storage.delete(self.image.name)
        # except: pass
        try:
            self.image.delete()
        except: pass
        super().delete()  
        

class Follow(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="employer_follows")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_follows")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        ordering = ('-pk',)
        db_table = 'follows' 
        
class SaveJob(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_save_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_save_jobs")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        ordering = ('-pk',)
        db_table = 'save_jobs'  

class Apply(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_applies")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_applies")
    status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        ordering = ('-pk',)
        db_table = 'applies'  
        
# Table educations
class Education(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_educations")
    #
    degree_name = models.CharField(max_length=255)
    major = models.CharField(max_length=255)
    university_name = models.CharField(max_length=255)
    gpa = models.FloatField()
    starting_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'educations'
    
    def __str__(self):
        return self.degree_name
    
# Table experiences
class Experience(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_experiences")
    #
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    job_location = models.CharField(max_length=255, null=True, blank=True)
    job_state = models.BooleanField()
    job_country = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'experiences'
    
    def __str__(self):
        return self.job_title
    
        
# Table skills
class Skill(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_skills")
    #
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'skills'
    
    def __str__(self):
        return self.name

# Table social_activities
class SocialActivity(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_social_activities")
    #
    title = models.CharField(max_length=255)
    unit_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    starting_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'social_activities'
    
    def __str__(self):
        return self.title
    
# Table certificates
class Certificate(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_certificates")
    #
    name = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'certificates'
    
    def __str__(self):
        return self.name