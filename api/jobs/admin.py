
from django.contrib import admin
from .models import *

# Register your models here.
class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 0
class JobAddressInline(admin.TabularInline):
    model = JobAddress
    extra = 0
    
class JobAdmin(admin.ModelAdmin):
    model = Job
    inlines = [BenefitInline, JobAddressInline]
    list_display = ['title', 'slug']
admin.site.register(Job, JobAdmin)

class JobTypeAdmin(admin.ModelAdmin):
    model = JobType
    list_display = ['name', 'slug']
admin.site.register(JobType, JobTypeAdmin)

class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ['pk', 'name', 'slug']
admin.site.register(Tag, TagAdmin)

class CountryAdmin(admin.ModelAdmin):
    model = Country
    list_display = ['name']
admin.site.register(Country, CountryAdmin)

class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ['name']
admin.site.register(City, CityAdmin)