from rest_framework import serializers
from db.models import District

class DistrictSerializer(serializers.ModelSerializer):
    district_id = serializers.CharField(source='id', read_only=True)
    updated_by = serializers.CharField( read_only=True)

    def create(self, validated_data):
        validated_data['updated_by'] = validated_data['created_by']
        return super().create(validated_data)
    class Meta:
        model = District
        fields = [
            'district_id',
            'name',
            'zone_id',
            'updated_by',
            'updated_at',
            'created_at',
            'created_by'
        ]