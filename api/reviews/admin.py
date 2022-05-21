
from django.contrib import admin
from .models import *

# Register your models here.
class ReviewInline(admin.TabularInline):
    model = Review

class ReviewAdmin(admin.ModelAdmin):
    model = Review
    list_display = ['title', 'point']
admin.site.register(Review, ReviewAdmin)

