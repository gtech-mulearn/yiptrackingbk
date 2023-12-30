from rest_framework.views import APIView
from .serializers import DistrictSerializer
from utils.response import CustomResponse
from utils.utils import CommonUtils
from db.models import District
from utils.authentication import JWTUtils
class DistrictAPI(APIView):
    def get(self, request):
        district = District.objects.all()
        paginated_queryset = CommonUtils.get_paginated_queryset(
            district,
            request,
            search_fields=['name'],
            sort_fields={'name':'name','created_at':'created_at','updated_at':'updated_at'},
            is_pagination=True
        )
        serializer = DistrictSerializer(paginated_queryset.get('queryset'), many=True)
        return CustomResponse().paginated_response(serializer.data, paginated_queryset.get('pagination'))
    
    def post(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        if not user_id:
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        serializer = DistrictSerializer(data=request.data,context={'user_id':user_id})
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='District created successfully').get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()