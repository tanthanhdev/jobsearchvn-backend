
from django.contrib import admin
from .models import *

# Register your models here.
class CvEducationInline(admin.TabularInline):
    model = CvEducation
class CvExperienceInline(admin.TabularInline):
    model = CvExperience
class CvSocialActivityInline(admin.TabularInline):
    model = CvSocialActivity
class CvCertificateInline(admin.TabularInline):
    model = CvCertificate  
class CvSkillInline(admin.TabularInline):
    model = CvSkill
class CvAdmin(admin.ModelAdmin):
    model = Cv
    search_fields = ['title']
    inlines= [CvEducationInline, CvExperienceInline,
              CvSocialActivityInline, CvCertificateInline, CvSkillInline]
    list_display = ['pk', 'title', 'user', 'cv_user_email']
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

class CvSkillAdmin(admin.ModelAdmin):
    model = CvSkill
    list_display = ['pk', 'name']
admin.site.register(CvSkill, CvSkillAdmin)

class CvCareerAdmin(admin.ModelAdmin):
    model = Cv_Career
    list_display = ['pk', 'name']
admin.site.register(Cv_Career, CvCareerAdmin)

class CvDesignAdmin(admin.ModelAdmin):
    model = Cv_Design
    list_display = ['pk', 'name']
admin.site.register(Cv_Design, CvDesignAdmin)