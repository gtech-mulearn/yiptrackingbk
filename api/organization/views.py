from rest_framework.views import APIView
from .serializers import OrganizationSerializer, UserOrgAssignSerializer, UserOrgVisitSerializer
from utils.response import CustomResponse
from utils.utils import ImportCSV, CommonUtils
from db.models import Organization, UserOrgLink, District, Zone
from utils.authentication import JWTUtils
import json
from django.db.models import Q, Sum, Value, F
from django.db.models.functions import Coalesce, Concat
from django.core.paginator import Page

# class UserIdeaViewCountAPI(APIView):
#     def get(self,request):
#         if not JWTUtils.is_jwt_authenticated(request):
#             return CustomResponse(general_message='Unauthorized').get_failure_response()
        
#         is_pagination = not (request.query_params.get('is_pagination', '').lower() in ('false','0'))
#         org_type = request.query_params.get('org_type')
#         district_id = request.query_params.get('district_id')
#         zone_id = request.query_params.get('zone_id')

#         data = UserOrgLink.objects.annotate(
#             email=F('user_id__email'),
#             full_name=Concat(F('user_id__first_name'), F('user_id__last_name')),
#             pre_registration=Coalesce(Sum('org_id__pre_registration'),Value(0)),
#             vos_completed=Coalesce(Sum('org_id__vos_completed'),Value(0)),
#             group_formation=Coalesce(Sum('org_id__group_formation'),Value(0)),
#             idea_submissions=Coalesce(Sum('org_id__idea_submissions'),Value(0)),
#         )
#         if org_type:
#             data = data.filter(org_id__org_type=org_type)
#         if district_id:
#             data = data.filter(org_id__district_id=district_id)
#         if zone_id:
#             data = data.filter(org_id__district_id__zone_id=zone_id)
#         data = data.values('full_name','email','pre_registration','vos_completed','group_formation','idea_submissions')
        
#         if is_pagination:
#             paginated_queryset : Page= CommonUtils.get_paginated_queryset(
#                 data, 
#                 request, 
#                 search_fields=['full_name', 'email'], 
#                 sort_fields={'full_name': 'full_name', 'email': 'email'},
#                 is_pagination=True
#             )
#             return CustomResponse().paginated_response(data=list(paginated_queryset.get('queryset')), pagination=paginated_queryset.get('pagination'))
#         return CustomResponse(response=list(data)).get_success_response()

# class OrganizationIdeaCountAPI(APIView):

#     def get(self,request):
#         if not JWTUtils.is_jwt_authenticated(request):
#             return CustomResponse(general_message='Unauthorized').get_failure_response()
#         zone_id = request.query_params.get('zone_id')
#         district_id = request.query_params.get('district_id')
#         org_type = request.query_params.get('org_type')
#         data_type = request.query_params.get('type') # intern, organization, district, zone
#         data_type = data_type if data_type else 'organization'
#         orgs = Organization.objects.all()
#         if zone_id:
#             orgs = orgs.filter(district_id__zone_id=zone_id)
#         if district_id:
#             orgs = orgs.filter(district_id=district_id)
#         if org_type:
#             orgs = orgs.filter(org_type=org_type)
#         if data_type == 'organization':
#             data = orgs.aggregate(
#                 pre_registration=Coalesce(Sum('pre_registration'),Value(0)),
#                 vos_completed=Coalesce(Sum('vos_completed'),Value(0)),
#                 group_formation=Coalesce(Sum('group_formation'),Value(0)),
#                 idea_submissions=Coalesce(Sum('idea_submissions'),Value(0)),
#             )
#         elif data_type == 'district':
#             data = orgs.values('district_id').annotate(
#                 district=F('district_id__name'),
#                 pre_registration=Coalesce(Sum('pre_registration'),Value(0)),
#                 vos_completed=Coalesce(Sum('vos_completed'),Value(0)),
#                 group_formation=Coalesce(Sum('group_formation'),Value(0)),
#                 idea_submissions=Coalesce(Sum('idea_submissions'),Value(0)),
#             )#.values('district','pre_registration','vos_completed','group_formation','idea_submissions')
#         return CustomResponse(response=data).get_success_response()

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


# class ImportOrgCSVAPI(APIView):

#     def post(self, request):
#         if not JWTUtils.is_jwt_authenticated(request):
#             return CustomResponse(general_message='Unauthorized').get_failure_response()
#         try:
#             file_obj = request.FILES["file"]
#         except KeyError:
#             return CustomResponse(
#                 general_message="File not found."
#             ).get_failure_response()

#         excel_data = ImportCSV()
#         excel_data = excel_data.read_excel_file(file_obj)

#         if not excel_data:
#             return CustomResponse(
#                 general_message="Empty csv file."
#             ).get_failure_response()

#         temp_headers = [
#             "code",
#             "pre_registration",
#             "vos_completed",
#             "group_formation",
#             "idea_submissions",
#         ]
#         first_entry = excel_data[0]
#         for key in temp_headers:
#             if key not in first_entry:
#                 return CustomResponse(
#                     general_message=f"{key} does not exist in the file."
#                 ).get_failure_response()

#         excel_data = [row for row in excel_data if any(row.values())]
#         print(json.dumps(excel_data, indent=4))
#         try:
#             for row in excel_data[1:]:
#                 org = Organization.objects.filter(code=row.get('code')).first()
#                 if org:
#                     org.pre_registration += row.get('pre_registration')
#                     org.vos_completed += row.get('vos_completed')
#                     org.group_formation += row.get('group_formation')
#                     org.idea_submissions += row.get('idea_submissions')
#                     org.save()
#                     continue
#                 return CustomResponse(general_message=f"Organization with code {row.get('code')} does not exist.").get_failure_response()
#             return CustomResponse(general_message=f"Successfully imported {len(excel_data[1:])} rows.").get_success_response()
#         except:
#             return CustomResponse(
#                 general_message="Error occured while importing data."
#             ).get_failure_response()