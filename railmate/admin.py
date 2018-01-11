from django.contrib import admin

# Register your models here.

from .models import Trip, Profile

admin.site.register(Trip)
admin.site.register(Profile)
