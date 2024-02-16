from rest_framework.views import APIView
from db.models import Organization, User
from utils.response import CustomResponse
from utils.authentication import JWTUtils
from django.db.models import Count, Sum, Value, F
from django.db.models.functions import Coalesce, Concat
from utils.utils import CSVUtils, CommonUtils, DateTimeUtils


class IdeaCountListAPI(APIView):
    def get(self, request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        zone_id = request.query_params.get('zone_id')
        district_id = request.query_params.get('district_id')
        org_type = request.query_params.get('org_type')
        data_type = request.query_params.get('type')  # organization, district, zone, intern
        data_type = data_type if data_type else 'organization'
        is_pagination = not (request.query_params.get('is_pagination', '').lower() in ('false', '0'))
        csv = request.query_params.get('csv', '').lower() in ('true', '1')

        if data_type == 'intern':
            orgs = User.objects.filter()
        else:
            orgs = Organization.objects.all()
            if zone_id:
                orgs = orgs.filter(district_id__zone_id=zone_id)
            if district_id:
                orgs = orgs.filter(district_id=district_id)
            if org_type:
                orgs = orgs.filter(org_type=org_type)
        sort_fields = {
            'pre_registration': 'pre_registration',
            'vos_completed': 'vos_completed',
            'group_formation': 'group_formation',
            'idea_submissions': 'idea_submissions'
        }
        search_fields = []
        if data_type == 'organization':
            data = orgs.values('id').annotate(
                name=Concat(F('code'), Value(' - '), F('title')),
                assigned_to=Concat(F('user_org_link_org_id__user_id__first_name'), Value(' '),
                                   F('user_org_link_org_id__user_id__last_name')),
                district=F('district_id__name'),
                assigned_to_email=F('user_org_link_org_id__user_id__email'),
                pre_registration=Coalesce(Sum('pre_registration'), Value(0)),
                vos_completed=Coalesce(Sum('vos_completed'), Value(0)),
                group_formation=Coalesce(Sum('group_formation'), Value(0)),
                idea_submissions=Coalesce(Sum('idea_submissions'), Value(0)),
            ).order_by('-idea_submissions').values('name', 'pre_registration', 'vos_completed', 'group_formation',
                                                   'idea_submissions', 'assigned_to', 'assigned_to_email', 'district')
            sort_fields['name'] = 'name'
            sort_fields['assigned_to'] = 'assigned_to'
            search_fields = ['name', 'assigned_to', 'assigned_to_email']
        if data_type == 'district':
            data = orgs.values('district_id').annotate(
                district=F('district_id__name'),
                zone=F('district_id__zone_id__name'),
                no_of_entries=Count('user_org_link_org_id'),
                pre_registration=Coalesce(Sum('pre_registration'), Value(0)),
                vos_completed=Coalesce(Sum('vos_completed'), Value(0)),
                group_formation=Coalesce(Sum('group_formation'), Value(0)),
                idea_submissions=Coalesce(Sum('idea_submissions'), Value(0)),
            ).order_by('-no_of_entries').values('district', 'zone', 'no_of_entries', 'pre_registration',
                                                'vos_completed', 'group_formation', 'idea_submissions')
            sort_fields['district'] = 'district'
            sort_fields['no_of_entries'] = 'no_of_entries'
            search_fields = ['district', 'zone']
        if data_type == 'zone':
            data = orgs.values('district_id__zone_id').annotate(
                zone=F('district_id__zone_id__name'),
                no_of_entries=Count('user_org_link_org_id'),
                pre_registration=Coalesce(Sum('pre_registration'), Value(0)),
                vos_completed=Coalesce(Sum('vos_completed'), Value(0)),
                group_formation=Coalesce(Sum('group_formation'), Value(0)),
                idea_submissions=Coalesce(Sum('idea_submissions'), Value(0)),
            ).order_by('-no_of_entries').values('zone', 'no_of_entries', 'pre_registration', 'vos_completed',
                                                'group_formation', 'idea_submissions')
            sort_fields['zone'] = 'zone'
            sort_fields['no_of_entries'] = 'no_of_entries'
            search_fields = ['zone']
        if data_type == 'intern':
            data = orgs.values('id').annotate(
                email=F('email'),
                district=F('district_id__name'),
                full_name=Concat(F('first_name'), F('last_name')),
                no_of_entries=Count('user_org_link_user_id'),
                pre_registration=Coalesce(Sum('user_org_link_user_id__org_id__pre_registration'), Value(0)),
                vos_completed=Coalesce(Sum('user_org_link_user_id__org_id__vos_completed'), Value(0)),
                group_formation=Coalesce(Sum('user_org_link_user_id__org_id__group_formation'), Value(0)),
                idea_submissions=Coalesce(Sum('user_org_link_user_id__org_id__idea_submissions'), Value(0)),
            ).order_by('-no_of_entries')
            if org_type:
                data = data.filter(user_org_link_user_id__org_id__org_type=org_type)
            if district_id:
                data = orgs.filter(user_org_link_user_id__org_id__district_id=district_id)
            if zone_id:
                data = orgs.filter(user_org_link_user_id__org_id__district_id__zone_id=zone_id)
            data = data.values('full_name', 'district', 'email', 'no_of_entries', 'pre_registration', 'vos_completed',
                               'group_formation', 'idea_submissions')
            sort_fields['full_name'] = 'full_name'
            sort_fields['district'] = 'district'
            sort_fields['email'] = 'email'
            sort_fields['no_of_entries'] = 'no_of_entries'
            search_fields = ['full_name', 'email']
        if csv:
            paginated_queryset = CommonUtils.get_paginated_queryset(
                data,
                request,
                search_fields=[],
                sort_fields=sort_fields,
                is_pagination=False
            )
            return CSVUtils.generate_csv(queryset=paginated_queryset,
                                         csv_name=f'IdeaView-{data_type}-{DateTimeUtils.get_current_utc_time().strftime("%Y-%m-%d")}')
        if is_pagination:
            paginated_queryset = CommonUtils.get_paginated_queryset(
                data,
                request,
                search_fields=search_fields,
                sort_fields=sort_fields,
                is_pagination=True
            )
            return CustomResponse().paginated_response(data=list(paginated_queryset.get('queryset')),
                                                       pagination=paginated_queryset.get('pagination'))
        return CustomResponse(response=data).get_success_response()


class TotalIdeaCountAPI(APIView):
    def get(self, request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        zone_id = request.query_params.get('zone_id')
        district_id = request.query_params.get('district_id')
        org_type = request.query_params.get('org_type')
        orgs = Organization.objects.all()
        if zone_id:
            orgs = orgs.filter(district_id__zone_id=zone_id)
        if district_id:
            orgs = orgs.filter(district_id=district_id)
        if org_type:
            orgs = orgs.filter(org_type=org_type)
        data = orgs.aggregate(
            pre_registration=Coalesce(Sum('pre_registration'), Value(0)),
            vos_completed=Coalesce(Sum('vos_completed'), Value(0)),
            group_formation=Coalesce(Sum('group_formation'), Value(0)),
            idea_submissions=Coalesce(Sum('idea_submissions'), Value(0)),
        )
        return CustomResponse(response=data).get_success_response()

class ImportOrgCSVAPI(APIView):
    def post(self, request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message='Unauthorized').get_failure_response()
        try:
            file_obj = request.FILES["file"]
        except KeyError:
            return CustomResponse(
                general_message="File not found."
            ).get_failure_response()

        excel_data = CSVUtils()
        excel_data = excel_data.read_excel_file(file_obj)
        if not excel_data:
            return CustomResponse(
                general_message="Empty csv file."
            ).get_failure_response()

        temp_headers = [
            "code",
            "pre_registration",
            "vos_completed",
            "group_formation",
            "idea_submissions",
        ]
        first_entry = excel_data[0]
        for key in temp_headers:
            if key not in first_entry:
                return CustomResponse(
                    general_message=f"{key} does not exist in the file."
                ).get_failure_response()

        excel_data = [row for row in excel_data if any(row.values())]
        try:
            has_error = False
            error_list = {}
            valid_list = []

            codes = list(Organization.objects.values_list('code', flat=True))
            for row in excel_data[1:]:
                code = row.get('code')
                if code not in codes:
                    has_error = True
                    error_list[code] = f"Organization with code '{code}' doesnt exist"
                    continue
                if error_list.get(code) or code in valid_list:
                    has_error = True
                    error_list[code] = f'Duplicate entry for code \'{code}\''
                    valid_list.remove(code)
                    continue
                valid_list.append(code)

            if has_error:
                return CustomResponse(general_message='\n'.join(error_list.values())).get_failure_response()
            for row in excel_data[1:]:
                Organization.objects.filter(code=row.get('code')).update(
                    pre_registration=row.get('pre_registration'),
                    vos_completed=row.get('vos_completed'),
                    group_formation=row.get('group_formation'),
                    idea_submissions=row.get('idea_submissions')
                )
            return CustomResponse(general_message=f"Successfully imported {len(excel_data[1:])} rows.").get_success_response()
        except:
            return CustomResponse(
                general_message="Error occured while importing data."
            ).get_failure_response()