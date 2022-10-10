from django.contrib import admin
from .models import *
from django.contrib.auth.models import User as UserCore


class UserAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'username', 'phone', 'email', 'is_superuser']
    fields = ['username', 'password', 'first_name', 'last_name', 'phone', 'email', 'telegram', 'is_staff',
              'is_superuser', 'last_login', 'date_joined']


class StatusAdmin(admin.ModelAdmin):
    list_display = ['importance', 'time', 'message']
    fields = ['importance', 'time', 'message']


admin.site.register(User, UserAdmin)
admin.site.register(CameraStatus, StatusAdmin)