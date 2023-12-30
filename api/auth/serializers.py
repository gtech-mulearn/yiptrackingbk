from rest_framework import serializers
from db.models import User
from django.contrib.auth.hashers import make_password
from db.models import UserOrgLink, Organization, District, Zone
from utils.types import OrgType
class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='id', read_only=True)
    password = serializers.CharField(write_only=True)
    assigned = serializers.SerializerMethodField(method_name='get_assigned')

    def create(self, validated_data):
        password = validated_data.pop("password")
        hashed_password = make_password(password)
        validated_data['password'] = hashed_password
        validated_data['updated_by'] = validated_data['created_by']
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
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
            'password',
            'gender',
            'dob',
            'district_id',
            'org_id',
            'assigned',
            'updated_at',
            'created_at',
            'created_by'
        ]
    
    def get_assigned(self, obj):
        assigned_orgs = UserOrgLink.objects.filter(user_id=obj.id)
        data = {
            'college':[],
            'school':[]
        }
        for org in assigned_orgs:
            if org.org_id.org_type == OrgType.COLLEGE.value:
                data['college'].append({
                    'org_id': org.org_id.id,
                    'title':org.org_id.title,
                    'code':org.org_id.code,
                    'visited':org.visited,
                    'pta':org.pta,
                    'alumni':org.alumni,
                    'association':org.association,
                    'whatsapp':org.whatsapp,
                    'participants':org.participants,
                    'visited_at':org.visited_at,
                    'district_id':org.org_id.district_id.id,
                    'district_name':org.org_id.district_id.name,
                    'zone_id':org.org_id.district_id.zone_id.id,
                    'zone_name':org.org_id.district_id.zone_id.name,
                })
            elif org.org_id.org_type == OrgType.SCHOOL.value:
                data['school'].append({
                    'org_id': org.org_id.id,
                    'title':org.org_id.title,
                    'code':org.org_id.code,
                    'visited':org.visited,
                    'pta':org.pta,
                    'alumni':org.alumni,
                    'association':org.association,
                    'whatsapp':org.whatsapp,
                    'participants':org.participants,
                    'visited_at':org.visited_at,
                    'district_id':org.org_id.district_id.id,
                    'district_name':org.org_id.district_id.name,
                    'zone_id':org.org_id.district_id.zone_id.id,
                    'zone_name':org.org_id.district_id.zone_id.name,
                })
        return data