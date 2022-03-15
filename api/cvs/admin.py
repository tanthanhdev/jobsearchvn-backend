
from django.contrib import admin
from .models import *

# Register your models here.
class CvAdmin(admin.ModelAdmin):
    model = Cv
    list_display = ['pk', 'user', 'cv_user_email']
admin.site.register(Cv, CvAdmin)

class CvEducationAdmin(admin.ModelAdmin):
    model = CvEducation
    list_display = ['pk', 'degree_name']
admin.site.register(CvEducation, CvEducationAdmin)

class CvExperienceAdmin(admin.ModelAdmin):
    model = CvExperience
    list_display = ['pk', 'job_title']
admin.site.register(CvExperience, CvExperienceAdmin)

class CvSocialActivityAdmin(admin.ModelAdmin):
    model = CvSocialActivity
    list_display = ['pk', 'title']
admin.site.register(CvSocialActivity, CvSocialActivityAdmin)

class CvCertificateAdmin(admin.ModelAdmin):
    model = CvCertificate
    list_display = ['pk', 'name']
admin.site.register(CvCertificate, CvCertificateAdmin)