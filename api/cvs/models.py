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
from api.members.models import Member

# Create your models here.
def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug

# Table cv_careers
class Cv_Career(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'cv_careers'
    
    def __str__(self):
        return self.name
    
# Table cv_designs
class Cv_Design(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'cv_designs'
    
    def __str__(self):
        return self.name

# Cv_Templates
class Cv_Template(models.Model):
    cv_career = models.ManyToManyField(Cv_Career, db_table='cv_templates_cv_carrers', related_name="cv_templates_cv_carrers")
    cv_design = models.ManyToManyField(Cv_Design, db_table='cv_templates_cv_designs', related_name="cv_templates_cv_designs")
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True)
    view = models.BigIntegerField(blank=True, default=0)
    status = models.CharField(max_length=100, blank=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'cv_templates'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # slug save
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        # ========================
        super(Cv_Template, self).save(*args, **kwargs)

# Table Cvs
class Cv(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="member_cvs")
    cv_template = models.ForeignKey(Cv_Template, on_delete=models.CASCADE, blank=True, null=True, related_name="cv_template_cv")
    cv_career = models.ManyToManyField(Cv_Career, db_table='cvs_cv_carrers')
    cv_design = models.ManyToManyField(Cv_Design, db_table='cvs_cv_designs')
    #
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True)
    view = models.BigIntegerField(blank=True, default=0)
    target_major = models.TextField()
    status = models.CharField(max_length=100, blank=True, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'cvs'
    
    def __str__(self):
        return self.title
    
    def cv_user_email(self):
        try:
            return self.member.user.email
        except:
            return None
    
    def save(self, *args, **kwargs):
            # slug save
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        # ========================
        super(Cv, self).save(*args, **kwargs)

# Table cv_educations
class CvEducation(models.Model):
    cv = models.ForeignKey(Cv, on_delete=models.CASCADE, related_name="cv_cv_educations", null=True, blank=True)
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
        db_table = 'cv_educations'
    
    def __str__(self):
        return self.degree_name
    
# Table cv_experiences
class CvExperience(models.Model):
    cv = models.ForeignKey(Cv, on_delete=models.CASCADE, related_name="cv_cv_experiences", null=True, blank=True)
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
        db_table = 'cv_experiences'
    
    def __str__(self):
        return self.job_title
    
        
# Table cv_skills
class CvSkill(models.Model):
    cv = models.ForeignKey(Cv, on_delete=models.CASCADE, related_name="cv_cv_skills", null=True, blank=True)
    #
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'cv_skills'
    
    def __str__(self):
        return self.name

# Table cv_social_activities
class CvSocialActivity(models.Model):
    cv = models.ForeignKey(Cv, on_delete=models.CASCADE, related_name="cv_cv_social_activities", null=True, blank=True)
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
        db_table = 'cv_social_activities'
    
    def __str__(self):
        return self.title
    
# Table cv_certificates
class CvCertificate(models.Model):
    cv = models.ForeignKey(Cv, on_delete=models.CASCADE, related_name="cv_cv_certificates", null=True, blank=True)
    #
    name = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'cv_certificates'
    
    def __str__(self):
        return self.name