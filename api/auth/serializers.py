from rest_framework import serializers
from db.models import User
from django.contrib.auth.hashers import make_password
from db.models import UserOrgLink
from utils.types import OrgType, Role
from utils.utils import DateTimeUtils

class UserListSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='id', read_only=True)
    password = serializers.CharField(write_only=True)
    district_name = serializers.CharField(source='district_id.name', read_only=True, default=None)
    org_name = serializers.CharField(source='org_id.title', read_only=True, default=None)

    class Meta:
        model = User
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'role',
            'email',
            'mobile',
            'password',
            'gender',
            'district_name',
            'org_name',
        ]

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='id', read_only=True)
    assigned = serializers.SerializerMethodField(method_name='get_assigned')
    district_name = serializers.CharField(source='district_id.name', read_only=True, default=None)
    org_name = serializers.CharField(source='org_id.title', read_only=True, default=None)
    zone_name = serializers.CharField(source='district_id.zone_id.name', read_only=True, default=None)

    def create(self, validated_data):
        password = f"yip@{validated_data['email']}"
        hashed_password = make_password(password)
        validated_data['password'] = hashed_password
        validated_data['updated_by'] = validated_data['created_by'] = self.context.get('user_id')
        validated_data['role'] = validated_data.get('role', Role.INTERN.value)
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.district_id = validated_data.get('district_id', instance.district_id)
        instance.org_id = validated_data.get('org_id', instance.org_id)
        instance.role = validated_data.get('role', instance.role)
        instance.updated_by = self.context.get('user_id')
        instance.updated_at = DateTimeUtils.get_current_utc_time()
        instance.save()
        return instance

    class Meta:
        model = User
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'role',
            'email',
            'mobile',
            'gender',
            'dob',
            'district_id',
            'district_name',
            'org_id',
            'org_name',
            'zone_name',
            'assigned'
        ]

    def get_assigned(self, obj):
        def append_org_data(org, org_type):
            return {
                'org_id': org.org_id.id,
                'title': org.org_id.title,
                'code': org.org_id.code,
                'visited': org.visited,
                'pta': org.pta,
                'alumni': org.alumni,
                'association': org.association,
                'whatsapp': org.whatsapp,
                'participants': org.participants,
                'visited_at': org.visited_at,
                'orientation': org.orientation,
                'is_scheduled': org.is_scheduled,
                'orientation_date': org.orientation_date,
                'scheduled_date': org.scheduled_date,
                'district_name': org.org_id.district_id.name,
                'zone_name': org.org_id.district_id.zone_id.name,
            }

        assigned_orgs = UserOrgLink.objects.filter(user_id=obj.id).prefetch_related('org_id').prefetch_related('org_id__district_id').prefetch_related('org_id__district_id__zone_id')

        data = {
            'college': [append_org_data(org, OrgType.COLLEGE.value) for org in assigned_orgs if
                        org.org_id.org_type == OrgType.COLLEGE.value],
            'school': [append_org_data(org, OrgType.SCHOOL.value) for org in assigned_orgs if
                       org.org_id.org_type == OrgType.SCHOOL.value],
            'iti': [append_org_data(org, OrgType.ITI.value) for org in assigned_orgs if
                    org.org_id.org_type == OrgType.ITI.value]
        }

        return data
