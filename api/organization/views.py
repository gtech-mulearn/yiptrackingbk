from rest_framework.views import APIView
from .serializers import OrganizationSerializer
from utils.response import CustomResponse
from utils.utils import CommonUtils
from db.models import Organization

class OrganizationAPI(APIView):
    def get(self, request):
        organizations = Organization.objects.all()
        paginated_queryset = CommonUtils.get_paginated_queryset(
            organizations,
            request,
            search_fields=['title','code'],
            sort_fields={'title':'title','code':'code','created_at':'created_at','updated_at':'updated_at'},
            is_pagination=True
        )
        serializer = OrganizationSerializer(paginated_queryset.get('queryset'), many=True)
        return CustomResponse().paginated_response(serializer.data, paginated_queryset.get('pagination'))
    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='Organziation created successfully').get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()