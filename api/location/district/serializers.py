from rest_framework import serializers
from db.models import District, User

class DistrictSerializer(serializers.ModelSerializer):
    district_id = serializers.CharField(source='id', read_only=True)

    def create(self, validated_data):
        validated_data['updated_by'] = validated_data['created_by'] = User.objects.get(id=self.context.get('user_id'))
        return super().create(validated_data)

    class Meta:
        model = District
        fields = [
            'district_id',
            'name',
            'zone_id',
        ]
