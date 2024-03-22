from django.contrib.auth import get_user_model, login
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework import viewsets, status, views, permissions
from . import reg_utils, reg_serializers, reg_model_serializers
from ..auth.auth_permissions import BaseAuthUserPermission
from ..mixins import SendOtpViewSetMixin, CommunicationViewSetObjectMixin
import datetime


class RegisterView(views.APIView):
    # http_method_names = ['post']

    def post(self, *args, **kwargs):
        default = {
            'created_at': datetime.datetime.now(),
            'is_blacklisted': False,
            'is_verified': False,
            'is_active': True
        }
        serializer = reg_model_serializers.UserLoginSerializer(data=self.request.data, context=default)
        if serializer.is_valid(raise_exception=True):
            user_login_data = serializer.validated_data
            instance = get_user_model().objects.create_user(**user_login_data)
            return Response({'message': 'ACCOUNT CREATED!'}, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': serializer.errors})

class LoginView(views.APIView):
    def post(self, request, format=None):
        serializer = reg_serializers.LoginSerializer(data=self.request.data, context={'request': self.request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            token_response = {'token': token.key, 'user_id': user.user_id}
            if user.is_verified == False:
                message = {'message': 'Verify your account before using our service!'}
                message['token'] = token.key
                message['user_id'] = user.user_id
                return Response(message, status=status.HTTP_202_ACCEPTED)
            return Response(token_response, status=status.HTTP_202_ACCEPTED)

class SendOtp(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        comm_method = request.data.get('method')
        instance = request.user
        comm_object_data = {
            'serializer': reg_serializers.OtpSerializer,
            'instance': instance,
            'user_id': instance.user_id,
            'comm_type': 'OTP',
            'subject': 'Your OTP',
        }
        comm_object = SendOtpViewSetMixin(**comm_object_data)
        otp = comm_object.generate_otp()
        comment = f'To finish creating your account, enter the OTP below: \n {otp}'
        comm_object.comment = comment
        request.session['otp'] = otp
        sr_data = {
            'otp': otp
        }
        if comm_object.send_otp(sr_data=sr_data, comm_method=comm_method):
            return Response({'message': 'OTP has been sent!'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'OTP not sent or method INVALID'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTP(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        otp = request.session.get('otp')
        user_otp = request.data.get('user-input-otp')
        if otp == user_otp:
            instance = request.user
            serializer = reg_model_serializers.UserLoginSerializer(instance=instance, data={'is_verified': True}, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'message': 'VALID OTP!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        request.session.set_expiry(300)

class UserAddressViewset(viewsets.ModelViewSet):
    permission_classes = [BaseAuthUserPermission]
    serializer_class = reg_model_serializers.UserAddressSerializer

    def get_queryset(self, request):
        user = self.request.user
        return UserAddresses.objects.filter(user_id=user)