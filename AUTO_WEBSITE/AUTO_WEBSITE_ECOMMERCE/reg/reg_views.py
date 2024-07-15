from django.contrib.auth import get_user_model, login, logout
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework import viewsets, status, views, permissions
from rest_framework.decorators import action
from . import reg_utils, reg_serializers, reg_model_serializers, reg_models
from ..auth.auth_permissions import BaseAuthUserPermission
from .. import mixins, exceptions, utils
import datetime
import re
from django.core.cache import cache

class LogoutView(views.APIView):
    def post(self, request):
        return reg_utils.logout(request)

class SensViewSet(mixins.TempMixin, mixins.CommunicationViewSetMixin, viewsets.ViewSet):

    def send_otp(self, request, **kwargs):
        comm_method = kwargs.get('method', None)
        if comm_method is not None:
            otp = super().generate_otp()
            request.session['otp'] = otp
            comment = kwargs.get('comment')
            comm_object_data = {
                'otp': otp,
                'comm_method': comm_method,
                'comment': f'{comment}, enter the OTP below\n {otp}',
                'user': kwargs.get('user')
            }
            otp_response = super().send_otp(request, **comm_object_data)
            return otp_response

    def verify_account(self, request):
        comm_method = request.data.get('method', None)
        if comm_method is not None:
            user = request.user
            request.session['reset_type'] = 'verify_account'
            return Response(self.send_otp(request, method=comm_method, comment=f'To verify your account', user=user), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reset(self, request):
        '''
        '''
        comm_method = request.data.get('method', None)
        reset_type = request.data.get('reset_type', None)
        if ((comm_method is not None) and (reset_type is not None)):
            request.session['reset_type'] = reset_type
            if comm_method == 'SMS':
                user_field = 'mobile_no'
            else:
                user_field = comm_method
                if user_field != 'email':
                    raise exceptions.invalid_error(obj_type='method type')
                if reset_type == 'email':
                    raise exceptions.invalid_error(obj_type='method type')
            user_field_data = request.data.get(user_field)
            url = request.path
            print(url)
            if 'user' in url:
                user_field = getattr(request.user, user_field)
                if user_field == user_field_data:
                    user = request.user
                else:
                    return Response({'message': 'False'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = reg_models.UserLogin.objects.get(**{user_field: user_field_data})
            request.session['user_id'] = user.pk
            self.send_otp(request, method=comm_method, comment=f'To reset your {reset_type}', user=user)
            return Response({'message': 'OTP sent'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        otp = request.session.get('otp')
        user_otp = request.data.get('user_input_otp')
        reset_type = request.session['reset_type']
        if otp == user_otp:
            otp_valid = True
            request.session['otp_valid'] = otp_valid
            if reset_type == 'verify_account':
                user = request.user
                if user is not None:
                    user.is_verified = True
                    user.save()
                else:
                    return Response({'message': 'gggg'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'VALID OTP!', 'details': f'{str(otp_valid)}, {str(reset_type)}'}, status=status.HTTP_200_OK)
        else:
            otp_valid = False
            request.session['otp_valid'] = otp_valid
            return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change(self, request):
        otp_valid = request.session['otp_valid']
        reset_type = request.session['reset_type']
        if otp_valid == True:
            user = reg_models.UserLogin.objects.get(pk=request.session.get('user_id'))
            new = request.data.get(f'new_{reset_type}')
            conf = request.data.get(f'confirm_{reset_type}')
            if new == conf:
                if (reset_type != 'password') and (reset_type != 'email'):
                    return Response({'message': 'Invalid reset type'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if reset_type == 'password':
                        user.set_password(conf)
                    else:
                        user.email = conf
                    user.save()
                    return reg_utils.logout(request)
            else:
                return Response({'message': f'{reset_type}s does not match!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'fuckoff', 'details': str(otp_valid)}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(views.APIView):
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
    def post(self, request):
        serializer = reg_serializers.LoginSerializer(data=self.request.data, context={'request': self.request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            message = {'message': 'Successfully logged in!'}
            if user.is_verified == False:
                message = {'message': 'Verify your account before using our service!'}
            response = Response()
            response.set_cookie(
                key='access_token',
                value=token.key,
                max_age=datetime.timedelta(days=10),
                httponly=True,
                samesite='Strict'
            )
            response.data = message
            response.status_code = status.HTTP_202_ACCEPTED
            return response

class VerifyViewSet(SensViewSet, viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    otp_valid = None
    reset_type = None

    def change(self, request):
        pass

    def reset(self, request):
        pass

    @action(detail=False, methods=['post'])
    def verify_account(self, request):
        return super().verify_account(request)
        
class UserDetailsViewSet(SensViewSet, mixins.DefaultCacheMixin, viewsets.ViewSet):

    permission_classes = [BaseAuthUserPermission]
    __parent_serializer = reg_model_serializers.UserDetailsSerializer
    __parent_model = reg_models.UserDetails

    custom_actions = ['change', 'reset', 'verify_otp']

    cache_list_fields = ['parent_model', 'user_id']

    def get_private(self, attrs):
        return utils.get_private(self=self, attrs=attrs)

    def list(self, request):
        user = self.request.user
        queryset = super().list_cache(queryset=self.__parent_model.objects, user_id=request.user.user_id).first()
        serializer = self.__parent_serializer(queryset)
        data = {**serializer.data, 'email': user.email, 'mobile_no': user.mobile_no}
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def __create(self, request, **kwargs):
        data = kwargs.get('data', None)
        request.method = 'POST'
        if data is not None:
            data['user_id'] = request.user.user_id
            serializer = self.__parent_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return True
    
    @action(detail=False, methods=['patch'], url_path=r'update')
    def custom_update(self, request, backend_req=False, **kwargs):
        user_id = self.request.user
        if backend_req:
            data = kwargs.get('data')
        else:
            data = request.data
        cache = super().list_cache(queryset=self.__parent_model.objects, user_id=request.user.user_id, return_cache_name=True)
        queryset = cache[0]
        if queryset is None:
            self.__create(request, data=data)
            if True:
                cache = super().list_cache(queryset=self.__parent_model.objects, user_id=request.user.user_id, return_cache_name=True)
                if not backend_req:
                    return Response({'message': 'Details Created'}, status=status.HTTP_200_OK)
                return True
        serializer = self.__parent_serializer(queryset[0], data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        super().delete_cache(cache_name=cache[1])
        if backend_req:
            return True
        else:
            return Response({'message': 'Details changed'}, status=status.HTTP_200_OK)

class UserAddressViewSet(UserDetailsViewSet, mixins.DefaultCacheMixin, viewsets.ViewSet):
    permission_classes = [BaseAuthUserPermission]

    __parent_serializer = reg_model_serializers.UserAddressesSerializer
    __parent_model = reg_models.UserAddresses

    custom_actions = ['change', 'reset', 'verify_otp']

    cache_list_fields = ['parent_model', 'user_id']

    def get_private(self, attrs):
        return utils.get_private(self=self, attrs=attrs)
        
    def list(self, request):
        print(self.get_private(['parent_model']))
        user = self.request.user
        queryset = super().list_cache(queryset=self.__parent_model.objects, user_id=request.user.user_id)
        serializer = self.__parent_serializer(queryset, many=True, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        user = request.user
        data = request.data
        default = {
            'user_id': user.user_id,
            'is_active': True,
            'is_default': False
        }
        data.update(**default)
        serializer = self.__parent_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            super().delete_cache(cache_type='list', user_id=user.user_id)
            return Response({'message': 'Address Created!'}, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        user = self.request.user
        queryset = super().list_cache(queryset=self.__parent_model.objects, user_id=user.user_id, return_cache_name=True)
        obj = queryset[0].filter(pk=pk).first()
        serializer = self.__parent_serializer(obj, data=request.data, partial=True)
        super().delete(cache_name=queryset[1])
        return Response({'message': 'Address Updated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def make_default(self, request, pk=None):
        user = self.request.user
        cache = super().list_cache(queryset=self.__parent_model.objects, user_id=user.user_id, return_cache_name=True)
        queryset = cache[0]
        current_default = queryset.filter(is_default=True).first()
        if current_default is not None:
            current_default.is_default = False
            current_default.save()
        new_default = queryset.filter(pk=pk).first()
        new_default.is_default = True
        new_default.save()
        default = {'default_address_id': pk}
        data = request.data
        if data is not None:
            default.update(**data)
        data = default
        print(data)
        super().custom_update(request, backend_req=True, data=data)
        if True:
            super().delete_cache(cache_name=cache[1])
            return Response({'message': 'Address Successfully made Default!'}, status=status.HTTP_200_OK)
        else:
            raise Exception