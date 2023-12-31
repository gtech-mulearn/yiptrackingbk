from django.contrib.auth.models import User
from django.db import models
import uuid


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=36, unique=True, null=False, default=uuid.uuid4)
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=False)
    role = models.CharField(max_length=150, null=True)
    email = models.EmailField(max_length=200, unique=True, null=False)
    password = models.CharField(max_length=100, null=False)
    mobile = models.CharField(max_length=15, null=True)
    gender = models.CharField(max_length=10, null=True)
    dob = models.DateField(null=True)
    district_id = models.ForeignKey('District', on_delete=models.CASCADE, null=True,
                                    related_name='user_district_id', db_column='district_id')
    org_id = models.ForeignKey('Organization', on_delete=models.CASCADE, null=True,
                               related_name='user_org_id', db_column='org_id')
    updated_by = models.CharField(max_length=36, null=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=36, null=False)

    class Meta:
        managed = False
        db_table = 'user'


class District(models.Model):
    id = models.CharField(primary_key=True, max_length=36, unique=True, null=False, default=uuid.uuid4)
    name = models.CharField(max_length=75, null=False)
    zone_id = models.ForeignKey('Zone', on_delete=models.CASCADE, null=False,
                                related_name='district_zone_id', db_column='zone_id')
    updated_by = models.ForeignKey('User', on_delete=models.CASCADE, null=False,
                                   related_name='district_updated_by', db_column='updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, null=False,
                                   related_name='district_created_by', db_column='created_by')

    class Meta:
        managed = False
        db_table = 'district'


class Zone(models.Model):
    id = models.CharField(primary_key=True, max_length=36, unique=True, null=False, default=uuid.uuid4)
    name = models.CharField(max_length=75, null=False)
    updated_by = models.ForeignKey('User', on_delete=models.CASCADE, null=False,
                                   related_name='zone_updated_by', db_column='updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, null=False,
                                   related_name='zone_created_by', db_column='created_by')

    class Meta:
        managed = False
        db_table = 'zone'


class Organization(models.Model):
    id = models.CharField(primary_key=True, max_length=36, unique=True, null=False, default=uuid.uuid4)
    title = models.CharField(max_length=100, null=False)
    code = models.CharField(max_length=12, null=False,unique=True)
    org_type = models.CharField(max_length=25, null=False)
    district_id = models.ForeignKey('District', on_delete=models.CASCADE, null=True,
                                    related_name='org_district_id', db_column='district_id')
    updated_by = models.ForeignKey('User', on_delete=models.CASCADE, null=False,
                                   related_name='org_updated_by', db_column='updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, null=False,
                                   related_name='org_created_by', db_column='created_by')

    class Meta:
        managed = False
        db_table = 'organization'


class UserOrgLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36, unique=True, null=False, default=uuid.uuid4)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE, null=False,
                                related_name='user_org_link_user_id', db_column='user_id')
    org_id = models.ForeignKey('Organization', on_delete=models.CASCADE, null=False,
                               related_name='user_org_link_org_id', db_column='org_id')
    visited = models.BooleanField(null=False, default=False)
    pta = models.CharField(max_length=255, null=True)
    alumni = models.CharField(max_length=255, null=True)
    association = models.CharField(max_length=255, null=True)
    whatsapp = models.CharField(max_length=255, null=True)
    participants = models.BigIntegerField(null=False, default=0)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, null=False,
                                   related_name='user_org_link_created_by', db_column='created_by')
    visited_at = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = 'user_org_link'
