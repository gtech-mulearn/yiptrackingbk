from django.contrib.auth.models import User
from django.db import models
# from django.contrib import admin
# from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import UserManager
from django.conf import settings
# Create your models here.
class CustomUser(models.Model):
  USERNAME_FIELD = "username"
  first_name = models.CharField(max_length=200,null=False,blank=False)
  last_name = models.CharField(max_length=100,null=False,blank=False)
  email = models.EmailField(unique=True,null=False,blank=False)
#   user_type = models.CharField(max_length=20,choices=(('ORG','Organization'),('USR','User')))
#   REQUIRED_FIELDS = ('first_name','last_name','email','password','user_type') 
