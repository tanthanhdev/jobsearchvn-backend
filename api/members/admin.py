
from django.contrib import admin
from .models import *

# Register your models here.
class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0
class SocialActivityInline(admin.TabularInline):
    model = SocialActivity
    extra = 0
class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0  
class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0
#
class MemberAdmin(admin.ModelAdmin):
    model = Member
    search_fields = ['resume']
    inlines= [EducationInline, ExperienceInline,
              SocialActivityInline, CertificateInline, SkillInline]
    list_display = ['user', 'member_user_email']
admin.site.register(Member, MemberAdmin)

class EducationAdmin(admin.ModelAdmin):
    model = Education
    list_display = ['pk', 'degree_name']
admin.site.register(Education, EducationAdmin)

class ExperienceAdmin(admin.ModelAdmin):
    model = Experience
    list_display = ['pk', 'job_title']
admin.site.register(Experience, ExperienceAdmin)

class SocialActivityAdmin(admin.ModelAdmin):
    model = SocialActivity
    list_display = ['pk', 'title']
admin.site.register(SocialActivity, SocialActivityAdmin)

class CertificateAdmin(admin.ModelAdmin):
    model = Certificate
    list_display = ['pk', 'name']
admin.site.register(Certificate, CertificateAdmin)

class SkillAdmin(admin.ModelAdmin):
    model = Skill
    list_display = ['pk', 'name']
admin.site.register(Skill, SkillAdmin)

class SaveJobAdmin(admin.ModelAdmin):
    model = SaveJob
    list_display = ['pk', 'job', 'member']
admin.site.register(SaveJob, SaveJobAdmin)

class ApplyAdmin(admin.ModelAdmin):
    model = Apply
    list_display = ['pk', 'job', 'member']
admin.site.register(Apply, ApplyAdmin)
class RegisterNotificationAdmin(admin.ModelAdmin):
    model = RegisterNotification
    list_display = ['pk', 'job_name', 'cron_job']
admin.site.register(RegisterNotification, RegisterNotificationAdmin)
