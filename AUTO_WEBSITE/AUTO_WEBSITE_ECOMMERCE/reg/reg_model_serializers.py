from rest_framework import serializers
from django.contrib.auth import get_user_model
from . import reg_models
from phonenumber_field import serializerfields

class UserLoginSerializer(serializers.ModelSerializer):
    mobile_no = serializerfields.PhoneNumberField()

    class Meta:
        model = reg_models.UserLogin
        fields = ['user_id', 'email', 'mobile_no', 'password', 'created_at', 'is_blacklisted', 'is_verified', 'is_active']

class UserAddressSerializer(serializers.ModelSerializer):
    mobile_no = serializerfields.PhoneNumberField()
    class Meta:
        model = reg_models.UserAddresses
        fields = ['address_id', 'user_id', 'name', 'unit_number', 'address_line_1', 'address_line_2', 'city', 'region', 'postal_code', 'mobile_no', 'is_regional', 'is_active']

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = reg_models.UserDetails
        fields = ['user_id', 'name', 'surname', 'company', 'default_address', 'company_reg_no', 'vat_no', 'is_synced', 'sage_id']