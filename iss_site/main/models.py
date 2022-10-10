from datetime import datetime

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser

from django.conf import settings


class User(AbstractUser):
    phone = PhoneNumberField(verbose_name='Номер телефона', null=True, blank=False, unique=True)
    telegram = models.IntegerField(verbose_name='Telegram UserID', null=True, unique=True, blank=True)


class CameraStatus(models.Model):
    importance = models.IntegerField()
    time = models.TimeField(default=datetime.now().time())
    message = models.CharField(max_length=255)
