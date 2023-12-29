# apps/management/api/serializers.py

from rest_framework import serializers,validators
from ..models import *

"""
User Serializer
"""
class UserSerializer(serializers.ModelSerializer):
    # first_name = serializers.CharField(required=True)
    # last_name = serializers.CharField(required=True)
    # user_type = serializers.CharField(required=True)
    # email = serializers.CharField(required=True,validators=[validators.UniqueValidator(queryset=CustomUser.objects.all())])
    # username = serializers.CharField(required=True,validators=[validators.UniqueValidator(queryset=CustomUser.objects.all())])
    # password = serializers.CharField(required=True)

    def create(self, validated_data):  
        """ 
        Create and return a new `Students` instance, given the validated data. 
        """  
        return CustomUser.objects.create(**validated_data)  
  
    def update(self, instance, validated_data):  
        """ 
        Update and return an existing `Students` instance, given the validated data. 
        """  
        instance.first_name = validated_data.get('first_name', instance.first_name)  
        instance.last_name = validated_data.get('last_name', instance.last_name)  
        instance.email = validated_data.get('email', instance.email)  
        instance.roll_number = validated_data.get('username', instance.username)  
        instance.password = validated_data.get('password', instance.password)  
        instance.user_type = validated_data.get('user_type',instance.user_type)
        instance.save()  
        return instance  
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','username','password','user_type']

class UserUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):  
        """ 
        Update and return an existing `Students` instance, given the validated data. 
        """  
        instance.first_name = validated_data.get('first_name', instance.first_name)  
        instance.last_name = validated_data.get('last_name', instance.last_name)  
        instance.email = validated_data.get('email', instance.email)  
        instance.roll_number = validated_data.get('username', instance.username)  
        instance.password = validated_data.get('password', instance.password)  
        instance.user_type = validated_data.get('user_type',instance.user_type)
        instance.save()  
        return instance  
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','username','password','user_type']

"""
Obtain Token Serializer
"""
class ObtainTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()