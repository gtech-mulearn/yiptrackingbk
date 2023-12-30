from rest_framework.views import APIView
from .serializers import ZoneSerializer
from utils.response import CustomResponse
from db.models import Zone
from utils.utils import CommonUtils
from utils.authentication import role_required
from utils.types import Role

class ZoneAPI(APIView):
    
    def get(self, request):
        zones = Zone.objects.all()
        paginated_queryset = CommonUtils.get_paginated_queryset(
            zones,
            request,
            search_fields=['name'],
            sort_fields={'name':'name','created_at':'created_at','updated_at':'updated_at'},
            is_pagination=True
        )
        serializer = ZoneSerializer(paginated_queryset.get('queryset'), many=True)
        return CustomResponse().paginated_response(serializer.data, paginated_queryset.get('pagination'))
    
    def post(self, request):
        serializer = ZoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='Zone created successfully').get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()