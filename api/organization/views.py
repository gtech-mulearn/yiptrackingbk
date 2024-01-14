from rest_framework.views import APIView
from .serializers import OrganizationSerializer, UserOrgAssignSerializer, UserOrgVisitSerializer
from utils.response import CustomResponse
from utils.utils import CommonUtils
from db.models import Organization, UserOrgLink
from utils.authentication import JWTUtils
from django.db.models import Q

class OrganizationListAPI(APIView):

    def get(self,request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        zone_id = request.query_params.get('zone_id')
        district_id = request.query_params.get('district_id')
        org_type = request.query_params.get('org_type')
        is_pagination = not (request.query_params.get('is_pagination', '').lower() in ('false','0'))
        
        orgs = Organization.objects.all()
        if zone_id:
            orgs = orgs.filter(district_id__zone_id=zone_id)
        if district_id:
            orgs = orgs.filter(district_id=district_id)
        if org_type:
            orgs = orgs.filter(org_type=org_type)
            
        if is_pagination:
            paginated_queryset = CommonUtils.get_paginated_queryset(
                orgs, 
                request, 
                search_fields=['title', 'code'], 
                sort_fields={'title': 'title', 'code': 'code'},
                is_pagination=True
            )
            serializer = OrganizationSerializer(instance=paginated_queryset.get('queryset'), many=True)
            return CustomResponse().paginated_response(data=serializer.data, pagination=paginated_queryset.get('pagination'))
        serializer = OrganizationSerializer(instance=orgs,many=True)
        return CustomResponse(response=serializer.data).get_success_response()


class OrganizationAPI(APIView):

    def get(self, request):
        organizations = Organization.objects.all()
        search = request.query_params.get('search')
        if search:
            organizations = organizations.filter(Q(title__icontains=search) | Q(code__icontains=search))
        serializer = OrganizationSerializer(organizations, many=True)
        return CustomResponse(response=serializer.data).get_success_response()

    def post(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        if not user_id:
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        serializer = OrganizationSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='Organziation created successfully').get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()


class AssignOrganizationAPI(APIView):

    # @role_required([Role.ADMIN])
    def post(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        if not user_id:
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        serializer = UserOrgAssignSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='Successfuly Assigned Organization').get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()


class OrgVisitedAPI(APIView):

    def post(self, request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        user_id = JWTUtils.fetch_user_id(request)
        org_id = request.data.get('org_id')
        if not org_id:
            return CustomResponse(general_message='Organization id is required').get_failure_response()
        uol = UserOrgLink.objects.filter(user_id=user_id, org_id=org_id).first()
        if not uol:
            return CustomResponse(general_message='Not assigned').get_failure_response()
        serializer = UserOrgVisitSerializer(instance=uol, data=request.data, context={'user_id': user_id}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='Successfuly Updated!').get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()