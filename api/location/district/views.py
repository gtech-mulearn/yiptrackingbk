from rest_framework.views import APIView
from .serializers import DistrictSerializer
from utils.response import CustomResponse
from utils.utils import CommonUtils
from db.models import District, UserOrgLink
from utils.authentication import JWTUtils
from django.db import connection
from django.db.models import Count, Sum, Value, IntegerField, Case, When, F
from django.db.models.functions import Coalesce

class DistrictAPI(APIView):
    def get(self, request):
        district = District.objects.all()
        # paginated_queryset = CommonUtils.get_paginated_queryset(
        #     district,
        #     request,
        #     search_fields=['name'],
        #     sort_fields={'name': 'name', 'created_at': 'created_at', 'updated_at': 'updated_at'},
        #     is_pagination=True
        # )
        serializer = DistrictSerializer(district, many=True)
        return CustomResponse(response=serializer.data).get_success_response()

    def post(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        if not user_id:
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        serializer = DistrictSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='District created successfully').get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()


class DistrictSummaryAPI(APIView):
    def get(self, request):
        district_id = request.query_params.get('district_id')
        zone_id = request.query_params.get('zone_id')
        org_type = request.query_params.get('org_type')
        district_summary = (
            UserOrgLink.objects
                .values(district_id=F('org_id__district_id'))
                .annotate(
                    district=F('org_id__district_id__name'),
                    no_of_entries=Count('id'),
                    visited=Sum(Case(When(visited=True, then=Value(1)), default=Value(0), output_field=IntegerField())),
                    participants=Coalesce(Sum('participants'),0),
                )
                .order_by('-no_of_entries')
        )
        if district_id:
            district_summary = district_summary.filter(org_id__district_id=district_id)
        if org_type:
            district_summary = district_summary.filter(org_id__org_type=org_type)
        if zone_id:
            district_summary = district_summary.filter(org_id__district_id__zone_id=zone_id)
        district_summary = district_summary.values('district','no_of_entries','visited','participants')
        result = list(district_summary)
        return CustomResponse(response=result).get_success_response()
