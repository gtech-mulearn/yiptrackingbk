# apps/management/authentication.py

from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
import decouple
from yiptracking.settings import SECRET_KEY
from .exceptions import UnauthorizedAccessException
from .utils import DateTimeUtils
from .response import CustomResponse

User = get_user_model()


class CustomizePermission(BasePermission):
    """
    Custom permission class to authenticate user based on bearer token.

    Attributes:
        token_prefix (str): The prefix of the token in the header.
        secret_key (str): The secret key to verify the token signature.
    """

    token_prefix = "Bearer"
    secret_key = SECRET_KEY

    def authenticate(self, request):
        """
        Authenticates the user based on the bearer token in the header.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            tuple: A tuple of (user, token_payload) if authentication is successful.

        Raises:
            UnauthorizedAccessException: If authentication fails.
        """
        return JWTUtils.is_jwt_authenticated(request)

    def authenticate_header(self, request):
        """
        Returns a string value for the WWW-Authenticate header.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            str: The value for the WWW-Authenticate header.
        """
        return f'{self.token_prefix} realm="api"'


class JWTUtils:

    @staticmethod
    def fetch_user_id(request):
        try:
            token = authentication.get_authorization_header(request).decode("utf-8").split()
            payload = jwt.decode(
                token[1], settings.SECRET_KEY, algorithms=["HS256"], verify=True
            )
            user_id = payload.get("id")
            if user_id is None:
                raise Exception(
                    "The corresponding JWT token does not contain the 'user_id' key"
                )
            return user_id
        except:
            return None

    @staticmethod
    def fetch_email(request):
        token = authentication.get_authorization_header(request).decode("utf-8").split()
        payload = jwt.decode(
            token[1], settings.SECRET_KEY, algorithms=["HS256"], verify=True
        )
        email = payload.get("email")
        if email is None:
            raise Exception(
                "The corresponding JWT token does not contain the 'email' key"
            )
        return email

    @staticmethod
    def fetch_role(request):
        token = authentication.get_authorization_header(request).decode("utf-8").split()
        payload = jwt.decode(
            token[1], settings.SECRET_KEY, algorithms=["HS256"], verify=True
        )
        role = payload.get("role")
        if role is None:
            raise Exception(
                "The corresponding JWT token does not contain the 'role' key"
            )
        return role

    @staticmethod
    def is_jwt_authenticated(request):
        token_prefix = "Bearer"
        secret_key = SECRET_KEY
        try:
            auth_header = authentication.get_authorization_header(request).decode("utf-8")
            if not auth_header or not auth_header.startswith(token_prefix):
                raise UnauthorizedAccessException("Invalid token header")

            token = auth_header[len(token_prefix):].strip()
            if not token:
                raise UnauthorizedAccessException("Empty Token")

            payload = jwt.decode(token, secret_key, algorithms=["HS256"], verify=True)

            user_id = payload.get("id")
            expiry = datetime.strptime(payload.get("expiry"), "%Y-%m-%d %H:%M:%S%z")

            if not user_id or expiry < DateTimeUtils.get_current_utc_time():
                raise UnauthorizedAccessException("Token Expired or Invalid")

            return None, payload
        except jwt.exceptions.InvalidSignatureError as e:
            raise UnauthorizedAccessException(
                {
                    "hasError": True,
                    "message": {"general": [str(e)]},
                    "statusCode": 1000,
                }
            ) from e
        except jwt.exceptions.DecodeError as e:
            raise UnauthorizedAccessException(
                {
                    "hasError": True,
                    "message": {"general": [str(e)]},
                    "statusCode": 1000,
                }
            ) from e
        except AuthenticationFailed as e:
            raise UnauthorizedAccessException(str(e)) from e
        except Exception as e:
            raise UnauthorizedAccessException(
                {
                    "hasError": True,
                    "message": {"general": [str(e)]},
                    "statusCode": 1000,
                }
            ) from e

    @staticmethod
    def is_logged_in(request):
        try:
            JWTUtils.is_jwt_authenticated(request)
            return True
        except UnauthorizedAccessException:
            return False


def role_required(roles):
    def decorator(view_func):
        def wrapped_view_func(obj, request, *args, **kwargs):
            roles = JWTUtils.fetch_role(request) 
            roles = roles if roles else []
            for role in roles:
                if role in roles:
                    response = view_func(obj, request, *args, **kwargs)
                    return response
            res = CustomResponse(
                general_message="You do not have the required role to access this page."
            ).get_failure_response()
            return res

        return wrapped_view_func
    return decorator

def string_to_date_time(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S%z")


def generate_jwt(user):
    access_expiry_time = DateTimeUtils.get_current_utc_time() + timedelta(hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])
    access_expiry = str(DateTimeUtils.format_time(access_expiry_time))

    access_token = jwt.encode(
        {
            'id': user.id, 
            'email': user.email, 
            'role':user.role if user.role else '',
            'expiry': access_expiry, 
            'tokenType': 'access'
        },
        decouple.config('SECRET_KEY'),
        algorithm="HS256")

    refresh_token = jwt.encode(
        {
            'id': user.id, 
            'email': user.email, 
            'tokenType': 'refresh'
        },
        decouple.config('SECRET_KEY'),
        algorithm="HS256")
    return access_token, refresh_token


def generate_access_token(user):
    access_expiry_time = DateTimeUtils.get_current_utc_time() + timedelta(seconds=10800)  # 3 hour
    access_expiry = str(DateTimeUtils.format_time(access_expiry_time))

    access_token = jwt.encode(
        {
            'id': user.id,
            'email': user.email, 
            'role':user.role,
            'expiry': access_expiry, 
            'tokenType': 'access'
        },
        decouple.config('SECRET_KEY'),
        algorithm="HS256")

    refresh_token = jwt.encode(
        {
            'id': user.id, 
            'email': user.email, 
            'tokenType': 'refresh'
        },
        decouple.config('SECRET_KEY'),
        algorithm="HS256")
    return access_token, refresh_token
