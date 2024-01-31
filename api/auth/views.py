from rest_framework import views
from .serializers import *
from django.http import HttpRequest
import decouple
import jwt
from datetime import timedelta
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.views import APIView
from django.db.models import Q
from utils.response import CustomResponse
from utils.authentication import generate_jwt, JWTUtils
from utils.utils import DateTimeUtils, CommonUtils
from db.models import User, Organization, UserOrgLink
from django.conf import settings
from utils.authentication import role_required
from utils.types import Role


class UserDeleteAPI(views.APIView):
    @role_required(roles=[Role.ADMIN.value, Role.DISTRICT_COORDINATOR.value])
    def delete(self, request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message="Not logged in!").get_failure_response()
        user_id = request.data.get('user_id')
        if not user_id:
            return CustomResponse(general_message="Invalid request, user id is required").get_failure_response()
        user = User.objects.filter(id=user_id).first()
        if not user:
            return CustomResponse(general_message="User doesn't exists").get_failure_response()
        if user.role != Role.INTERN.value:
            return CustomResponse(general_message="Only interns can be deleted").get_failure_response()
        user.delete()
        return CustomResponse(general_message="User deleted successfully").get_success_response()


class UserAssignDeleteAPI(views.APIView):
    @role_required(roles=[Role.ADMIN.value, Role.DISTRICT_COORDINATOR.value, Role.ZONE_COORDINATOR.value])
    def delete(self, request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message="Not logged in!").get_failure_response()
        user_id = request.data.get('user_id')
        org_id = request.data.get('org_id')
        if not user_id:
            return CustomResponse(general_message="Invalid request, user id is required").get_failure_response()
        user = User.objects.filter(id=user_id).first()
        if not user:
            return CustomResponse(general_message="User doesn't exists").get_failure_response()
        if not org_id:
            return CustomResponse(general_message="Invalid request, org id is required").get_failure_response()
        org = Organization.objects.filter(id=org_id).first()
        if not org:
            return CustomResponse(general_message="Organization doesn't exists").get_failure_response()
        result = UserOrgLink.objects.filter(user_id=user_id, org_id=org_id).first()
        result.delete()
        return CustomResponse(general_message="Deleted").get_success_response()


class PasswordResetAPI(views.APIView):
    def patch(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        if not user_id:
            return CustomResponse(general_message="Unauthorized").get_failure_response()
        if user := User.objects.filter(id=user_id).first():
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            if not old_password or not new_password:
                return CustomResponse(general_message="Invalid request").get_failure_response()
            if not check_password(old_password, user.password):
                return CustomResponse(general_message="Invalid password").get_failure_response()
            user.password = make_password(new_password)
            user.save()
            return CustomResponse(general_message="Password set successfully").get_success_response()
        else:
            return CustomResponse(general_message="Invalid user").get_failure_response()


class UserListAPI(views.APIView):
    def get(self, request):
        users = User.objects.all()
        search_query = request.query_params.get("search")
        if search_query:
            q1 = Q(first_name__icontains=search_query)
            q2 = Q(last_name__icontains=search_query)
            q3 = Q(email__icontains=search_query)
            users = users.filter(q1 | q2 | q3)

        paginated_queryset = CommonUtils.get_paginated_queryset(
            queryset=users,
            request=request,
            search_fields=['first_name', 'last_name', 'email', 'mobile'],
            sort_fields={'first_name': 'first_name', 'last_name': 'last_name', 'email': 'email', 'mobile': 'mobile',
                         'created_at': 'created_at', 'updated_at': 'updated_at', 'role': 'role'},
        )

        serializer = UserListSerializer(instance=paginated_queryset.get('queryset'), many=True)
        return CustomResponse().paginated_response(data=serializer.data,
                                                   pagination=paginated_queryset.get('pagination'))


class UserRegisterAPI(views.APIView):
    def get(self, request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message="Not logged in!").get_failure_response()
        email = request.query_params.get('email')
        if email:
            user = User.objects.filter(email=email).first()
        else:
            user_id = JWTUtils.fetch_user_id(request)
            if not user_id:
                return CustomResponse(general_message="Invalid token!").get_success_response()
            user = User.objects.filter(id=user_id).first()
        if not user:
            return CustomResponse(general_message="Invalid user").get_success_response()
        serializer = UserSerializer(instance=user, many=False)
        return CustomResponse(message=serializer.data).get_success_response()

    def post(self, request):
        if not JWTUtils.is_jwt_authenticated(request):
            return CustomResponse(general_message="Not logged in!").get_failure_response()
        user_id = JWTUtils.fetch_user_id(request)
        serializer = UserSerializer(data=request.data, context={'user_id': user_id})
        if not serializer.is_valid():
            return CustomResponse(general_message="Invalid Request", message=serializer.errors).get_failure_response()
        serializer.save()
        return CustomResponse(general_message='User created successfully').get_success_response()

    def put(self, request: HttpRequest):
        user_id = JWTUtils.fetch_user_id(request)
        if not user_id:
            return CustomResponse(general_message="Unauthorized").get_failure_response()
        instance = User.objects.filter(id=user_id).first()
        if instance == None:
            return CustomResponse(general_message='User not found').get_failure_response()
        serializer = UserSerializer(instance=instance, data=request.data, partial=True, context={'user_id': user_id})
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(general_message='User updated successfully').get_success_response()
        else:
            return CustomResponse(general_message="Invalid data!", message=serializer.errors).get_failure_response()


class UserAuthenticationAPI(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return CustomResponse(general_message="Please provide a valid email and password").get_failure_response()
        if user := User.objects.filter(email=email).first():
            if user.password and check_password(password, user.password):
                access_token, refresh_token = generate_jwt(user)
                return CustomResponse(
                    response={'accessToken': access_token, 'refreshToken': refresh_token,
                              'roles': user.role}).get_success_response()
            else:
                return CustomResponse(general_message="Invalid password").get_failure_response()
        else:
            return CustomResponse(general_message="Invalid email").get_failure_response()


class GetAccessToken(APIView):
    def post(self, request):
        refresh_token = request.data.get('refreshToken')
        try:
            payload = jwt.decode(refresh_token, decouple.config('SECRET_KEY'), algorithms="HS256", verify=True)
        except Exception as e:
            return CustomResponse(general_message=str(e)).get_failure_response()

        email = payload.get('email')
        token_type = payload.get('tokenType')

        if token_type != "refresh":
            return CustomResponse(general_message="Invalid refresh token").get_failure_response(1003)

        if email:
            user = User.objects.filter(email=email).first()
            if not user:
                return CustomResponse(general_message="User invalid").get_failure_response(1004)

            access_expiry_time = DateTimeUtils.get_current_utc_time() + timedelta(
                hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])  # 3 hour
            access_expiry = access_expiry_time.strftime("%Y-%m-%d %H:%M:%S%z")
            access_token = jwt.encode(
                {
                    'id': user.id,
                    'email': user.email,
                    'expiry': access_expiry,
                    'tokenType': 'access'
                },
                decouple.config('SECRET_KEY'),
                algorithm="HS256")
            return CustomResponse(response={'accessToken': access_token, 'refreshToken': refresh_token,
                                            'expiry': access_expiry}).get_success_response()
        else:
            return CustomResponse(general_message="Invalid token").get_failure_response()
