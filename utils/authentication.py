# apps/management/authentication.py

from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError
import decouple, pytz

User = get_user_model()

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
    



def format_time(date_time):
    formated_time = date_time.strftime("%Y-%m-%d %H:%M:%S%z")
    return datetime.strptime(formated_time, "%Y-%m-%d %H:%M:%S%z")


def get_current_utc_time() -> datetime:
    """
    Returns the current time in UTC.

    Returns:
        datetime.datetime: The current time in UTC.
    """
    local_now = datetime.now(pytz.timezone("UTC"))

    return format_time(local_now)


def string_to_date_time(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S%z")


def generate_jwt(user):
    access_expiry_time = get_current_utc_time() + timedelta(seconds=10800)  # 3 hour
    access_expiry = str(format_time(access_expiry_time))

    access_token = jwt.encode(
        {'id': user.id, 'email': user.email,'expiry': access_expiry, 'tokenType': 'access'},
        decouple.config('SECRET_KEY'),
        algorithm="HS256")

    refresh_token = jwt.encode(
        {'id': user.id, 'email': user.email,'tokenType': 'refresh'},
        decouple.config('SECRET_KEY'),
        algorithm="HS256")
    return access_token, refresh_token


def generate_access_token(user):

    access_expiry_time = get_current_utc_time() + timedelta(seconds=10800)  # 3 hour
    access_expiry = str(format_time(access_expiry_time))

    access_token = jwt.encode(
        {'id': user.id, 'email': user.email,'expiry': access_expiry, 'tokenType': 'access'},
        decouple.config('SECRET_KEY'),
        algorithm="HS256")

    refresh_token = jwt.encode(
        {'id': user.id, 'email': user.email,'tokenType': 'refresh'},
        decouple.config('SECRET_KEY'),
        algorithm="HS256")
    return access_token, refresh_token

