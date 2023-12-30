from rest_framework import serializers
from db.models import Organization, UserOrgLink, User
from utils.utils import DateTimeUtils

class OrganizationSerializer(serializers.ModelSerializer):
    org_id = serializers.CharField(source='id', read_only=True)
    updated_by = serializers.CharField( read_only=True)

    def create(self, validated_data):
        validated_data['updated_by'] = validated_data['created_by']
        return super().create(validated_data)
    
    class Meta:
        model = Organization
        fields = [
            'org_id',
            'title',
            'code',
            'district_id',
            'updated_by',
            'updated_at',
            'created_at',
            'created_by'
        ]

class UserOrgVisitSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    org_id = serializers.CharField(read_only=True)
    id = serializers.CharField(read_only=True)
    created_at = serializers.DateField(read_only=True)
    created_by = serializers.CharField(read_only=True)

    class Meta:
        model = UserOrgLink
        fields = [
            'id',
            'user_id',
            'org_id',
            'visited',
            'pta',
            'alumni',
            'association',
            'whatsapp',
            'participants',
            'visited_at',
            'created_at',
            'created_by'
        ]

class UserOrgAssignSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data['created_by'] = User.objects.filter(id=self.context.get('user_id')).first()
        return super().create(validated_data)
    class Meta:
        model = UserOrgLink
        fields = [
            'user_id',
            'org_id'
        ]