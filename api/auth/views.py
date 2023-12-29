from rest_framework import views, status
from rest_framework.response import Response
from .serializers import *
from db.models import User
from django.http import HttpRequest
from utils.response import CustomResponse
import decouple
import jwt
from datetime import timedelta
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView

from utils.response import CustomResponse
from utils.authentication import generate_jwt, JWTUtils
from utils.utils import DateTimeUtils
from db.models import User


class UserRegisterAPI(views.APIView):
    def get(self, request):
        email = request.data.get('email')
        if not email:
            return CustomResponse(general_message="Invalid email").get_success_response()

        serializer = UserSerializer(instance=User.objects.filter(email=email).first(), many=False)
        return CustomResponse(message=serializer.data).get_success_response()

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(general_message="Invalid Request", message=serializer.errors).get_failure_response()
        serializer.save()
        return CustomResponse(general_message='User created successfully').get_success_response()

    # def put(self, request:HttpRequest ):
    #     instance = User.objects.filter(username=request.POST.get('email',None)).first()
    #     if instance == None:
    #         return CustomResponse(general_message='User not found').get_failure_response()
    #     serializer = UserSerializer(instance=instance,data=request.data) 
    #     if serializer.is_valid():  
    #         serializer.update() 
    #         return CustomResponse(general_message='User updated successfully',message=serializer.data).get_success_response()
    #     else:  
    #         return CustomResponse(general_message="Invalid data!",message=serializer.data)


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
                    response={'accessToken': access_token, 'refreshToken': refresh_token}).get_success_response()
            else:
                return CustomResponse(general_message="Invalid password").get_failure_response()
        else:
            return CustomResponse(general_message="Invalid muid or email").get_failure_response()


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

            access_expiry_time = DateTimeUtils.get_current_utc_time() + timedelta(seconds=10800)  # 3 hour
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
