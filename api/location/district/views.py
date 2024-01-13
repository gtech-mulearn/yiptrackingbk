from rest_framework.views import APIView
from .serializers import DistrictSerializer
from utils.response import CustomResponse
from utils.utils import CommonUtils
from db.models import District
from utils.authentication import JWTUtils
from django.db import connection


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
        q1 = """WITH DistrictSummary AS (
                    SELECT
                        d.name AS District,
                        COUNT(uol.id) AS No_of_entries,
                        SUM(CASE WHEN uol.visited = True THEN 1 ELSE 0 END) AS visited,
                        IFNULL(SUM(uol.participants),0) AS participants
                    FROM
                        user_org_link uol
                        INNER JOIN organization o ON uol.org_id = o.id
                        RIGHT JOIN district d ON o.district_id = d.id
                    """
        q2 = """\n
        GROUP BY
            d.name
        ORDER BY No_of_entries
                    DESC
                    )
                    SELECT * FROM DistrictSummary"""
        q = ""
        if district_id:
            q = f"\nWHERE d.id = '{district_id}' "
        if zone_id:
            q +=f"\nWHERE d.zone_id = '{zone_id}' " if not q.endswith(" ") else f"AND d.zone_id = '{zone_id}' "
        if org_type:
            q = f"\nWHERE o.org_type = '{org_type}' " if not q.endswith(" ") else f"AND d.org_type = {zone_id} "
        
        query = q1 + q + q2
        data = []
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            data.extend(
                {
                    'district': row[0],
                    'no_of_entries': row[1],
                    'visited': int(row[2]),
                    'participants': int(row[3]),
                }
                for row in rows
            )
        return CustomResponse(response=data).get_success_response()
