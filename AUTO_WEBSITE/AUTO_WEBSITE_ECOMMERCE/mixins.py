import datetime, os, random, string, inspect
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework import viewsets, status
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from . import utils, serializers as custom_serializers
from twilio.rest import Client
import requests
from django.db.models import Prefetch
import re
from django.core.cache import cache

class CommunicationViewSetMixin():
    admin_email = 'office@autolectronix.co.za'
    serializer_data = None
    parent_serializer = None
    comm_history_serializer = None
    instance = None
    user_id = None
    email = None
    mobile_no = None
    obj_type = None
    type_id = None
    comm_type = None
    subject = None
    date = None
    comment = None

    def initialize_comm_object(self, request, is_admin_req=False, **kwargs):
        if is_admin_req == True:
            self.user_id = kwargs.get('user_id', None)
            if self.user_id is not None:
                user_details = self.get_user_details()
                self.email = user_details['email']
                self.mobile_no = user_details['mobile_no']
            self.parent_serializer = kwargs.get('parent_serializer', None)
            self.comm_history_serializer = kwargs.get('comm_history_serializer', None)
        else:
            if request.user.is_authenticated:
                user = request.user
            else:
                user = kwargs.get('user')
            self.user_id = user.pk
            self.email = user.email
            self.mobile_no = user.mobile_no
        self.serializer_data = kwargs.get('serializer_data', None)
        self.instance = kwargs.get('instance', None)
        self.type_id = kwargs.get('type_id', None)
        self.comm_type = kwargs.get('comm_type', None)
        self.subject = kwargs.get('subject', None)
        self.date = utils.return_date_and_time()
        self.comment = kwargs.get('comment', None)

    def get_user_details(self):
        user_id = UserLogin.objects.get(user_id=self.user_id)
        mobile_no = user_id.mobile_no
        email = user_id.email
        data = {
            'mobile_no': f'{mobile_no}',
            'email': email
        }
        return data

    def perform_send_email(self, attachment=None, admin_email=False):
        try:
            subject = f'{self.subject}'
            comment = f'{self.comment}'
            from_email = 'alex@autolectronix.co.za'
            recipient_list = [self.email]
            if admin_email is True:
                recipient_list.append(self.admin_email)
            email = EmailMessage(subject, comment, from_email=from_email, to=recipient_list)
            # email = EmailMultiAlternatives(subject, comment, from_email=from_email, to=recipient_list)
            # html_message = render_to_string(html_file)
            # email.attach_alternative(html_message, 'text/html')
            # if attachment is not None:
            #     email.attach_file(attachment)
            email.send(fail_silently=False)
            # utils.delete_file(html_file)
            return True
        except:
            return False

    def perform_send_sms(self):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_mobile_no = settings.TWILIO_MOBILE_NO

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body = f'{self.subject}: {self.comment}',
            from_ = twilio_mobile_no,
            to = str(self.mobile_no)
        )

    def save_to_comm_history(self, comm_method, comm_recipient):
        sr_data = {
            'user_id': self.user_id,
            f'{self.obj_type}_id': self.type_id,
            'comm_method': comm_method,
            'comm_type': self.comm_type,
            'comm_recipient': comm_recipient,
            'comm_date': self.date,
            'comm_subject': self.subject,
            'comm_comment': self.comment
        }
        serializer = self.serializer_comm_history(data=sr_data)
        return serializer.save()

    def send_email(self, attachment=None):
        date = self.date
        comm_type = self.comm_type
        type_id = self.type_id
        filename = utils.generate_filename(type_id, comm_type, date)
        html_email_data = {
            'obj_type': self.obj_type,
            'type_id': type_id,
            'filename': filename,
            'html_template_type': comm_type,
            'subject': self.subject,
            'comment': self.comment,
        }
        email_serializer = custom_serializers.HTMLEmailSerializer(data=html_email_data)
        if email_serializer.is_valid(raise_exception=True):
            email_render_data = {**self.serializer_data, **email_serializer.data}
            email_render_request = requests.post(url='http://host.docker.internal:8080/html-email', json=email_render_data)
            email_render_message = email_render_request.json()['message']
            if email_render_message == 'render successful':
                print('sending message')
                # html_file = utils.return_file(filedir='html/', filename=f'{filename}.html', return_file=True)
                # if True:
                self.perform_send_email()
                if True:
                    if self.serializer_comm_history is not None:
                        self.save_to_comm_history(comm_method='email', comm_recipient=self.email, admin_email=kwargs.get('admin_email', False))
                    message = {'message': 'successful'}
                    return message
                else:
                    message = {'message': 'email not sent'}
                    return message
                # else:
                #     message = {'message': 'file not found'}
                #     return message
            else:
                message = {'message': 'render not successful'}
                return message

    def send_sms(self):
        self.perform_send_sms()
        if self.comm_history_serializer is not None:
            self.save_to_comm_history(comm_method='SMS', comm_recipient=self.mobile_no)

    def check_method(self, comm_method, attachment=None):
        if comm_method == 'SMS':
            return self.send_sms()
        if comm_method == 'email':
            return self.send_email(attachment)
        if comm_method == 'SMS, email':
            self.send_sms()
            return self.send_email(attachment)
        else:
            return False

    def update_status(self, request, is_admin_req=False, **kwargs):
        instance = kwargs.get('instance', None)
        type_id = getattr(instance, f'{self.obj_type}_id')
        comm_object_data = {
            'type_id': type_id,
            'instance': instance,
            'comm_type': 'status',
            'subject': kwargs.get('subject', None),
            'comment': kwargs.get('comment', None)
        }
        if is_admin_req:
            comm_object_data['user_id'] = instance.user_id
        self.initialize_comm_object(request, is_admin_req=is_admin_req, **comm_object_data)
        comm_method = kwargs.get('comm_method', None)
        if comm_method is not None:
            status_data = {
                'current_status_id': kwargs.get('current_status_id', None),
                'current_status_date': self.date,
                'current_status_comment': self.comment
            }
            serializer = self.serializer_status(self.instance, data=status_data, partial=True)
            # status_data[f'{self.obj_type}_id'] = self.type_id
            # status_data['obj_type'] = self.obj_type
            self.serializer_data = status_data
            self.check_method(comm_method)
            serializer.save()

    def send_conf(self, request, **kwargs):
        instance = kwargs.get('instance', None)
        type_id = getattr(instance, f'{self.obj_type}_id')
        comm_object_data = {
            'type_id': type_id,
            'comm_type': 'conf',
            'serializer_data': kwargs.get('serializer_data', None),
            'subject': kwargs.get('subject', None),
            'comment': kwargs.get('comment', None)
        }
        self.initialize_comm_object(request, **comm_object_data)
        return self.send_email(admin_email=True)

    def generate_otp(self, length=6):
        characters = string.digits
        otp = ''.join(random.choice(characters) for _ in range(length))
        return otp

    def send_otp(self, request, **kwargs):
        comm_method = kwargs.get('comm_method', None)
        otp = kwargs.get('otp', None)
        if ((comm_method is not None) and (otp is not None)):
            comm_object_data = {
                'comm_type': 'OTP',
                'subject': 'Your OTP',
                'comment': kwargs.get('comment', None),
                'serializer_data': {'otp': otp}
            }
            self.initialize_comm_object(request, user=kwargs.get('user', None), **comm_object_data)
            # self.serializer_data = otp
            return self.check_method(comm_method)

class DefaultCacheMixin():

    def __get_class_var(self, class_str):
        class_var = getattr(self, class_str, None)
        if class_var is None:
            try:
                class_var = self.get_private([class_str])
                if not class_var:
                    class_var = class_str
            except Exception:
                class_var = class_str
        return class_var

    def __convert_model_name(self, model):
        '''
        get model name and convert it from string or class name into lowercase
        '''
        model_name = self.__get_class_var(model)
        if type(model_name) != str:
            model_name = getattr(model_name, '__name__', None)
        model_name = re.sub(r'([A-Z])', r'_\1', model_name).lower()
        return model_name

    def __create_cache_name(self, **kwargs):
        '''
        create cache name, format = 'model_field=value'
        '''
        model = kwargs.get('model')
        fields = kwargs.get('fields', None)
        if fields is not None:
            for key, value in fields.items():
                model += f'_{key}={value}'
        return model

    def __get_fields(self, **kwargs):
        '''
        get fields for cache, checks if model is actually model
        '''
        cache_type = kwargs.get('cache_type', None)
        model = None
        fields = {}
        if cache_type is not None:
            cache_name = getattr(self, f'cache_{cache_type}_fields', None)
            print(cache_name)
            if cache_name is not None:
                model = self.__convert_model_name(cache_name.pop(0))
                for name in cache_name:
                    attr = self.__get_class_var(name)
                    fields.update(**{attr: kwargs.get(attr)})
            else:
                raise Exception
        extra_fields = kwargs.get('extra_fields', {})
        fields.update(**extra_fields)
        return [model, fields]

    def __initialize(self, **kwargs):
        '''
        initialize cache fields, name and model, returns fields and cache name
        '''
        model, fields = self.__get_fields(**kwargs)
        if model is None:
            model = kwargs.get('model', None)
            model = self.__convert_model_name(model)
        cache_name = self.__create_cache_name(model=model, fields=fields)
        return [fields, cache_name]

    def get_or_set(self, **kwargs):
        '''
        uses django cache.get_or_set function, 
        initializes cache name and fields beforehand if cache name isn't provided
        has optional parameter to return cache name if initialized in function
        '''
        cache_name = kwargs.get('cache_name', None)
        if cache_name is None:
            initialize = self.__initialize(**kwargs)
            cache_name = initialize[1]
            fields = initialize[0]
        else:
            fields = self.__get_fields(extra_fields=kwargs.get('fields'))
        queryset = kwargs.get('queryset', None)
        data = kwargs.get('data', None)
        return_cache_name = kwargs.get('return_cache_name', False)
        if data is None:
            data = queryset.filter(**fields)
        cache_data = cache.get(cache_name)
        if cache_data is None:
            if data:
                cache.set(cache_name, data)
                cache_data = data
            else:
                cache_data = None
        print(cache_data)
        if return_cache_name:
            return [cache_data, cache_name]
        else:
            return cache_data

    def delete_cache(self, **kwargs):
        '''
        deletes cache from provided cache name, otherwise initializes cache name then deletes cache
        '''
        cache_name = kwargs.get('cache_name', None)
        if cache_name is None:
            initialize = self.__initialize(**kwargs)
            cache_name = initialize[1]
        return cache.delete(cache_name)

    def list_cache(self, **kwargs):
        '''
        default cache for list()
        '''
        kwargs['cache_type'] = 'list'
        delete = kwargs.get('delete', False)
        if delete:
            return self.delete_cache(**kwargs)
        return self.get_or_set(**kwargs)

    def retrieve_cache(self, **kwargs):
        '''
        default cache for retrieve()
        '''
        kwargs['cache_type'] = 'retrieve'
        return self.get_or_set(**kwargs)

    def __inner_filter(self, data, **kwargs):
        key = kwargs.get('key')
        value = kwargs.get('value')
        data_type = kwargs.get('data_type', 'str')
        if data_type != 'str':
            if data_type == 'int':
                value = int(value)
            if data_type == 'float':
                value = float(value)
            if data_type == 'decimal':
                value = dec(value)
        print(value)
        output_data = [d for d in data if getattr(d, key) == value]
        print(output_data)
        return output_data

    def filter_cache(self, data, **kwargs):
        '''
        to filter cache, uses pythonic filter instead of django filtering
        (django filtering hits the database)
        first filters queryset, is saved to 'filtered_data' then 'filtered_data' filters itself after that
        '''
        fields = kwargs.get('fields', None)
        if fields is not None:
            print(fields)
            filtered_data = None
            for i in range(len(fields)):
                for field in fields:
                    print(field)
                    for key, value in field.items():
                        if key == 'data_type':
                            data_type = value
                        else:
                            main_key = key
                            main_value = value
                    main_kwargs = {
                        'key': main_key,
                        'value': main_value,
                        'data_type': data_type
                    }
                    if i != 0:
                        data = filtered_data
                    filtered_data = self.__inner_filter(data=data, **main_kwargs)
            return filtered_data

class Temp():
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

class TempMixin():
    temp_name = None

    def __make_temp_name__(self, request):
        user = request.user
        name = f'__temp_{self.temp_name}_user_id={user.user_id}'
        return name

    def init_temp(self, request, **kwargs):
        temp = Temp()
        name = self.__make_temp_name__(request)
        cache.set(name, temp)
        return temp

    def get_temp(self, request):
        name = self.__make_temp_name__(request)
        temp = cache.get(name, None)
        return temp

    def set_temp(self, request, temp):
        name = self.__make_temp_name__(request)
        temp = cache.set(name, temp)
        return temp

    def delete_temp(self, request, temp):
        name = self.__make_temp_name__(request)
        return cache.delete(name)

# class CommunicationViewSetObjectMixin():
#     def __init__(self, is_admin_req=False, **kwargs):
#         self.serializer = kwargs.get('serializer')
#         self.serializer_add = kwargs.get('serializer_add')
#         self.serializer_comm_history = kwargs.get('serializer_comm_history')
#         self.instance = kwargs.get('instance')
#         self.user_id = kwargs.get('user_id')
#         self.obj_type = kwargs.get('obj_type')
#         self.type_id = kwargs.get('type_id')
#         self.comm_type = kwargs.get('comm_type')
#         self.subject = kwargs.get('subject')
#         self.date = utils.return_date_and_time()
#         self.comment = kwargs.get('comment')
#         if is_admin_req == False:
#             self.email = kwargs.get('email')
#             self.mobile_no = str(kwargs.get('mobile_no'))
#         else:
#             self.get_user_details()

#     def get_user_details(self):
#         user_id = UserLogin.objects.filter(user_id=self.user_id).first()
#         mobile_no = user_id.mobile_no
#         email = user_id.email
#         data = {
#             'mobile_no': f'{mobile_no}',
#             'email': email
#         }
#         for key, value in data.items():
#             setattr(self, key, value)
 
#     # def return_email(self, filename):
#     #     html_file = os.path.join(settings.MEDIA_ROOT, f'html/{filename}.html')
#     #     if os.path.isfile(html_file):
#     #         open(html_file)
#     #         return True
#             # return Response(data={'message': 'Email Successfully Rendered!'}, status=status.HTTP_200_OK)
#         # else:
#         #     return False
#             # return Response(data={'message': 'Email Not Rendered'}, status=status.HTTP_400_BAD_REQUEST)

#     def perform_send_email(self, html_file, attachment):
#         try:
#             subject = f'{self.subject}'
#             comment = f'{self.comment}'
#             from_email = settings.EMAIL_HOST_USER
#             recipient_list = [self.email]
#             email = EmailMultiAlternatives(subject, comment, from_email=from_email, to=recipient_list)
#             html_message = render_to_string(html_file)
#             email.attach_alternative(html_message, 'text/html')
#             if attachment is not None:
#                 email.attach_file(attachment)
#             email.send()
#             utils.delete_file(html_file)
#             return True
#         except:
#             return False

#     def perform_send_sms(self):
#         account_sid = settings.TWILIO_ACCOUNT_SID
#         auth_token = settings.TWILIO_AUTH_TOKEN
#         twilio_mobile_no = settings.TWILIO_MOBILE_NO

#         client = Client(account_sid, auth_token)
#         message = client.messages.create(
#             body = f'{self.subject}: {self.comment}',
#             from_ = twilio_mobile_no,
#             to = self.mobile_no
#         )
    
#     def save_to_comm_history(self, comm_recipient):
#         sr_data = {
#             'user_id': self.user_id,
#             f'{self.obj_type}_id': self.type_id,
#             'comm_method': comm_method,
#             'comm_type': self.comm_type,
#             'comm_recipient': comm_recipient,
#             'comm_date': self.date,
#             'comm_subject': self.subject,
#             'comm_comment': self.comment
#         }
#         serializer = self.serializer_comm_history(data=sr_data)
#         serializer.save()

#     # def send_email(self, sr_data, sr_data_add, attachment):
#     #     self.render_email(sr_data=sr_data, sr_data_add=sr_data_add)
#     #     filename = request.session.get('filename')
#     #     html_file = self.return_email(filename)
#     #     self.perform_send_email(html_file, attachment)
#     #     if self.serializer_comm_history is not None:
#     #         self.save_to_comm_history(comm_method='email', comm_recipient=self.email)

#     def send_email(self, sr_data, sr_data_add, attachment=None):
#         date = self.date
#         comm_type = self.comm_type
#         type_id = self.type_id
#         filename = utils.generate_filename(type_id, comm_type, date)
#         html_email_data = {
#             'type_id': type_id,
#             'filename': filename,
#             'html_template_type': comm_type,
#             'subject': self.subject,
#             'comment': self.comment
#         }
#         serializer_2 = serializers.HTMLEmailSerializer(data=html_email_data)
#         if serializer_2.is_valid(raise_exception=True):
#             if sr_data is None:
#                 serializer_add = self.serializer_add(data=sr_data_add, many=True)
#                 if serializer_add.is_valid(raise_exception=True):
#                     serializer_data = {**serializer_add.data, **serializer_2.data}
#             elif sr_data_add is None:
#                 serializer = self.serializer(data=sr_data)
#                 if serializer.is_valid(raise_exception=True):
#                     serializer_data = {**serializer.data, **serializer_2.data}
#             elif sr_data is None and sr_data_add is None:
#                 serializer_data = serializer_2
#             else:
#                 serializer = self.serializer(data=sr_data)
#                 serializer_add = self.serializer_add(data=sr_data_add, many=True)
#                 if serializer.is_valid(raise_exception=True) and serializer_add.is_valid(raise_exception=True):
#                     serializer_data = {**serializer.data, **serializer_add.data, **serializer_2.data}
#             r = requests.post(url='http://host.docker.internal:8080/html-email', json=serializer_data)
#             r_message = r.json()['message']
#             if r_message == 'render successful':
#                 # html_file = self.return_email(filename)
#                 html_file = utils.return_file(filedir='html/', filename=f'${filename}.html', return_file=True)
#                 if True:
#                     self.perform_send_email(html_file, attachment)
#                     if True:
#                         if self.serializer_comm_history is not None:
#                             self.save_to_comm_history(comm_method='email', comm_recipient=self.email)
#                         message = {'message': 'successful!'}
#                         return message
#                     else:
#                         message = {'message': 'email not sent'}
#                         return message
#                 else:
#                     message = {'message': 'file not found'}
#                     return message
#             else:
#                 message = {'message': 'render_unsuccessful'}
#                 return message

#     def send_sms(self):
#         self.perform_send_sms()
#         if self.comm_type != 'OTP':
#             self.save_to_comm_history(comm_method='SMS', comm_recipient=self.mobile_no)

# class UpdateStatusViewSetMixin(CommunicationViewSetObjectMixin):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def update_status(self, current_status_id, comm_method):
#         sr_data = {
#             'current_status_id': current_status_id,
#             'current_status_date': self.date,
#             'current_status_comment': self.comment
#         }
#         sr_data_add = {
#             f'{self.obj_type}_id': self.type_id
#         } + sr_data
#         serializer = self.serializer(self.instance, data=sr_data, partial=True)
#         if comm_method == 'SMS':
#             self.send_sms()
#         if comm_method == 'email':
#             self.send_email(sr_data=None, data_add=sr_data_add)
#         if comm_method == 'SMS, email':
#             self.send_sms()
#             self.send_email(sr_data=None, data_add=sr_data_add)
#         serializer.save()

# class SendEmailConfViewSetMixin(CommunicationViewSetObjectMixin):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def render_conf(self, sr_data, sr_data_add=None):
#         if sr_data_add is not None:
#             return self.send_email(sr_data=sr_data, sr_data_add=sr_data_add)
#         else:
#             return self.send_email(sr_data=sr_data, sr_data_add=None)
#         # if self.obj_type == 'order':
#         #     sr_data_add = {}
#         #     prefetch_query = Prefetch('sku_no__product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id'))
#         #     OrderItems.objects.filter.prefetch_related(prefetch_query).filter(order_id=self.type_id)
#         #     return self.send_email(sr_data=sr_data, sr_data_add=sr_data_add)
#         # else:
#         #     return self.send_email(sr_data=sr_data, sr_data_add=None)

# class SendOtpViewSetMixin(CommunicationViewSetObjectMixin):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def generate_otp(self, length=6):
#         characters = string.digits
#         otp = ''.join(random.choice(characters) for _ in range(length))
#         return otp

#     def send_otp(self, sr_data, comm_method):
#         if comm_method == 'SMS':
#             if self.send_sms():
#                 return True
#         if comm_method == 'email':
#             otp_response = self.send_email(sr_data=sr_data, sr_data_add=None)
#             return otp_response
#             # if self.send_email(sr_data=sr_data, sr_data_add=None):
#             #     return True
#         else:
#             return False
#         # if comm_method == 'SMS, email':
#         #     self.send_sms()
#         #     self.send_email(sr_data=sr_data, sr_data_add=None)