from rest_framework import serializers
from db.models import Organization, UserOrgLink, User


class OrganizationSerializer(serializers.ModelSerializer):
    org_id = serializers.CharField(source='id', read_only=True)
    updated_by = serializers.CharField(read_only=True)
    created_by = serializers.CharField(read_only=True)

    def create(self, validated_data):
        validated_data['updated_by'] = validated_data['created_by'] = User.objects.filter(
            id=self.context.get('user_id')).first()
        return super().create(validated_data)

    class Meta:
        model = Organization
        fields = [
            'org_id',
            'title',
            'code',
            'org_type',
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
    email = serializers.EmailField(write_only=True)
    org_id = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        org_ids = validated_data.pop('org_id', [])

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("No user found with this email")

        created_by_user = User.objects.filter(id=self.context.get('user_id')).first()
        user_org_links = []

        for org_id in org_ids:
            user_org_link_data = {
                'user_id': user,
                'org_id': Organization.objects.filter(id=org_id).first(),
                'created_by': created_by_user
            }
            if UserOrgLink.objects.filter(user_id=user, org_id=org_id).exists():
                raise serializers.ValidationError("User is already assigned to this organization")

            user_org_link = UserOrgLink.objects.create(**user_org_link_data)
            user_org_links.append(user_org_link)

        return user_org_links

    class Meta:
        model = UserOrgLink
        fields = [
            'org_id',
            'email'
        ]
