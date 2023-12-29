# apps/management/authentication.py

from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, ParseError
import decouple, pytz
from yiptracking.settings import SECRET_KEY
from .exceptions import UnauthorizedAccessException
from .utils import DateTimeUtils

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


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract the JWT from the Authorization header
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        if jwt_token is None:
            return None

        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)  # clean the token

        # Decode the JWT and verify its signature
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except:
            raise ParseError()

        # Get the user from the database
        username_or_phone_number = payload.get('user_identifier')
        if username_or_phone_number is None:
            raise AuthenticationFailed('User identifier not found in JWT')

        user = User.objects.filter(username=username_or_phone_number).first()
        if user is None:
            raise AuthenticationFailed('User not found')

        # Return the user and token payload
        return user, payload

    def authenticate_header(self, request):
        return 'Bearer'

    @classmethod
    def create_jwt(cls, user):
        # Create the JWT payload
        payload = {
            'user_identifier': user.username,
            'exp': int((datetime.now() + timedelta(hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])).timestamp()),
            # set the expiration time for 5 hour from now
            'iat': datetime.now().timestamp(),
            'username': user.username,
            'email': user.email
        }

        # Encode the JWT with your secret key
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return jwt_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')  # clean the token
        return token


def string_to_date_time(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S%z")


def generate_jwt(user):
    access_expiry_time = DateTimeUtils.get_current_utc_time() + timedelta(seconds=10800)  # 3 hour
    access_expiry = str(DateTimeUtils.format_time(access_expiry_time))

    access_token = jwt.encode(
        {'id': user.id, 'email': user.email, 'expiry': access_expiry, 'tokenType': 'access'},
        decouple.config('SECRET_KEY'),
        algorithm="HS256")

    refresh_token = jwt.encode(
        {'id': user.id, 'email': user.email, 'tokenType': 'refresh'},
        decouple.config('SECRET_KEY'),
        algorithm="HS256")
    return access_token, refresh_token


def generate_access_token(user):
    access_expiry_time = DateTimeUtils.get_current_utc_time() + timedelta(seconds=10800)  # 3 hour
    access_expiry = str(DateTimeUtils.format_time(access_expiry_time))

    access_token = jwt.encode(
        {'id': user.id, 'email': user.email, 'expiry': access_expiry, 'tokenType': 'access'},
        decouple.config('SECRET_KEY'),
        algorithm="HS256")

    refresh_token = jwt.encode(
        {'id': user.id, 'email': user.email, 'tokenType': 'refresh'},
        decouple.config('SECRET_KEY'),
        algorithm="HS256")
    return access_token, refresh_token
