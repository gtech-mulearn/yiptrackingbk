from rest_framework import serializers
from db.models import Organization, UserOrgLink, User


class OrganizationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id',
            'name',
            'code',
            'pre_registration',
            'vos_completed',
            'group_formation',
            'idea_submissions',
        ]

    def get_name(self, obj):
        return f"{obj.code} - {obj.title}"


class UserOrgVisitSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    org_id = serializers.CharField(read_only=True)
    id = serializers.CharField(read_only=True)

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
