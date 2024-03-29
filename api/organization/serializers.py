from rest_framework import serializers
from db.models import Organization, UserOrgLink, User

class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id',
            'title',
            'code',
            'district_id',
            'org_type'
        ]
    def create(self, validated_data):
        user_id = self.context.get('user_id')
        user = User.objects.filter(id=user_id).first()
        validated_data['created_by'] = user
        validated_data['updated_by'] = user
        return Organization.objects.create(**validated_data)

class OrganizationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()
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
            'assigned_to'
        ]


    def get_name(self, obj):
        return f"{obj.code} - {obj.title}"
    
    def get_assigned_to(self, obj):
        assigned =  UserOrgLink.objects.filter(org_id=obj.id).values_list('user_id__first_name','user_id__last_name').prefetch_related('user_id__first_name','user_id__last_name')
        return ' '.join(assigned[0]) if len(assigned) > 0 else None

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
            'is_scheduled',
            'orientation',
            'orientation_date',
            'scheduled_date',
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
