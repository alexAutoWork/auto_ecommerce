from rest_framework import serializers
from django.contrib.auth import get_user_model
from . import reg_models
from phonenumber_field import serializerfields
from .. import serializer_fields

class UserLoginSerializer(serializers.ModelSerializer):
    mobile_no = serializerfields.PhoneNumberField()

    class Meta:
        model = reg_models.UserLogin
        fields = '__all__'

class UserAddressesSerializer(serializers.ModelSerializer):
    contact_number = serializerfields.PhoneNumberField()
    class Meta:
        model = reg_models.UserAddresses
        fields = '__all__'

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = reg_models.UserDetails
        fields = '__all__'