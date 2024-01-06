from rest_framework import serializers
from db.models import Zone, User


class ZoneSerializer(serializers.ModelSerializer):
    zone_id = serializers.CharField(source='id', read_only=True)

    def create(self, validated_data):
        validated_data['updated_by'] = validated_data['created_by'] = User.objects.get(id=self.context.get('user_id'))
        return super().create(validated_data)

    class Meta:
        model = Zone
        fields = [
            'zone_id',
            'name',
        ]
