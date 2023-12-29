from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
import uuid

class User(models.Model):
  id = models.CharField(primary_key=True,max_length=36,unique=True,null=False,blank=False,default=uuid.uuid4)
  first_name = models.CharField(max_length=150,null=False,blank=False)
  last_name = models.CharField(max_length=150,null=False,blank=False)
  role = models.CharField(max_length=150,null=True,blank=False)
  email = models.EmailField(max_length=200,unique=True,null=False,blank=False)
  password = models.CharField(max_length=100,null=False,blank=False)
  mobile = models.CharField(max_length=15,null=True,blank=False)
  gender = models.CharField(max_length=10,null=True,blank=False)
  dob = models.DateField(null=True,blank=False)
  district_id = models.ForeignKey('District',on_delete=models.CASCADE,null=True,blank=False)
  org_id = models.ForeignKey('Organization',on_delete=models.CASCADE,null=True,blank=False)
  updated_by = models.ForeignKey('User',on_delete=models.CASCADE,null=False,blank=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now=True)
  created_by = models.ForeignKey('User',on_delete=models.CASCADE,null=False,blank=False)

  class Meta:
      managed = False
      db_table = 'user'

class District(models.Model):
  id = models.CharField(primary_key=True,max_length=36,unique=True,null=False,blank=False,default=uuid.uuid4)
  name = models.CharField(max_length=75,null=False,blank=False)
  zone_id = models.ForeignKey('Zone',on_delete=models.CASCADE,null=False,blank=False)
  updated_by = models.ForeignKey('User',on_delete=models.CASCADE,null=False,blank=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now=True)
  created_by = models.ForeignKey('User',on_delete=models.CASCADE,null=False,blank=False)

  class Meta:
      managed = False
      db_table = 'district'

class Zone(models.Model):
  id = models.CharField(primary_key=True,max_length=36,unique=True,null=False,blank=False,default=uuid.uuid4)
  name = models.CharField(max_length=75,null=False,blank=False)
  updated_by = models.ForeignKey('User',on_delete=models.CASCADE,null=False,blank=False)
  updated_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now=True)
  created_by = models.ForeignKey('User',on_delete=models.CASCADE,null=False,blank=False)

  class Meta:
      managed = False
      db_table = 'zone'
