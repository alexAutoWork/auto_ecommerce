from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from phonenumber_field import serializerfields
from . import reg_model_serializers
from django.forms.models import model_to_dict

# User Creation Model Serializers

class OtpSerializer(serializers.Serializer):
    otp = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(default=None)
    mobile_no = serializerfields.PhoneNumberField(default=None)
    password = serializers.CharField(max_length=500)

    def validate(self, attrs):
        email = attrs.get('email')
        mobile_no = attrs.get('mobile_no')
        password = attrs.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, mobile_no=mobile_no, password=password)

            if not user:
                msg = 'Access denied: wrong email, mobile number or password'
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'Both an email or mobile number and password are required.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs