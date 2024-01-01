from rest_framework.views import APIView
from .serializers import OrganizationSerializer, UserOrgAssignSerializer, UserOrgVisitSerializer
from utils.response import CustomResponse
from utils.utils import CommonUtils
from db.models import Organization, UserOrgLink
from utils.authentication import JWTUtils


class OrganizationListAPI(APIView):

    def get(self, request):
        if not (org_type := request.query_params.get('org_type')):
            return CustomResponse(general_message='Invalid Request').get_failure_response()
        organizations = Organization.objects.filter(org_type=org_type)
        serializer = OrganizationSerializer(organizations, many=True)
        return CustomResponse(response=serializer.data).get_success_response()


class OrganizationAPI(APIView):

    def get(self, request):
        organizations = Organization.objects.all()
        paginated_queryset = CommonUtils.get_paginated_queryset(
            organizations,
            request,
            search_fields=['title', 'code'],
            sort_fields={'title': 'title', 'code': 'code', 'created_at': 'created_at', 'updated_at': 'updated_at'},
            is_pagination=True
        )
        serializer = OrganizationSerializer(paginated_queryset.get('queryset'), many=True)
        return CustomResponse().paginated_response(serializer.data, paginated_queryset.get('pagination'))

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
