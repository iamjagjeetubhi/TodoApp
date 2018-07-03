from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from urllib.request import urlopen, HTTPError
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.html import escape, mark_safe
import datetime


class User(AbstractUser):
    country = CountryField(blank=True)

class TodoList(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    content = models.TextField(blank=True)
    created = models.DateTimeField(default=timezone.now) 
    class Meta:
        ordering = ["-created"]
    def __str__(self):
        return self.title

