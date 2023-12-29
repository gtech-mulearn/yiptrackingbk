from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
import uuid


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100, unique=True, null=False, blank=False, default=uuid.uuid4)
    email = models.EmailField(unique=True, null=False, blank=False)
    password = models.CharField(max_length=100, null=False, blank=False)
    first_name = models.CharField(max_length=200, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
