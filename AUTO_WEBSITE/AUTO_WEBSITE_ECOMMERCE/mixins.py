import datetime, os, random, string
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from . import utils, serializers
from twilio.rest import Client
from .reg.reg_models import UserLogin
from .auth.auth_models import OrderItems
from .auth.auth_model_serializers import OrderItemsSerializer
import requests

class CommunicationViewSetObjectMixin(viewsets.ViewSet):
    def __init__(self, **kwargs):
        self.serializer = kwargs.get('serializer')
        self.serializer_add = kwargs.get('serializer_add')
        self.serializer_comm_history = kwargs.get('serializer_comm_history')
        self.instance = kwargs.get('instance')
        self.user_id = kwargs.get('user_id')
        self.get_user_details()
        self.obj_type = kwargs.get('obj_type')
        self.type_id = kwargs.get('type_id')
        self.comm_type = kwargs.get('comm_type')
        self.subject = kwargs.get('subject')
        self.date = utils.return_date_and_time()
        self.comment = kwargs.get('comment')

    def get_user_details(self):
        user_id = UserLogin.objects.filter(user_id=self.user_id).first()
        mobile_no = user_id.mobile_no
        email = user_id.email
        data = {
            'mobile_no': f'{mobile_no}',
            'email': email
        }
        for key, value in data.items():
            setattr(self, key, value)
 
    def return_email(self, filename):
        html_file = os.path.join(settings.MEDIA_ROOT, f'html/{filename}.html')
        if os.path.isfile(html_file):
            open(html_file)
            return True
            # return Response(data={'message': 'Email Successfully Rendered!'}, status=status.HTTP_200_OK)
        else:
            return False
            # return Response(data={'message': 'Email Not Rendered'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_send_email(self, html_file, attachment):
        try:
            subject = f'{self.subject}'
            comment = f'{self.comment}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [self.email]
            email = EmailMultiAlternatives(subject, comment, from_email=from_email, to=recipient_list)
            html_message = render_to_string(html_file)
            email.attach_alternative(html_message, 'text/html')
            if attachment is not None:
                email.attach_file(attachment)
            email.send()
            utils.delete_file(html_file)
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
            to = self.mobile_no
        )
    
    def save_to_comm_history(self, comm_recipient):
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
        serializer.save()

    # def send_email(self, sr_data, sr_data_add, attachment):
    #     self.render_email(sr_data=sr_data, sr_data_add=sr_data_add)
    #     filename = request.session.get('filename')
    #     html_file = self.return_email(filename)
    #     self.perform_send_email(html_file, attachment)
    #     if self.serializer_comm_history is not None:
    #         self.save_to_comm_history(comm_method='email', comm_recipient=self.email)

    def send_email(self, sr_data, sr_data_add, attachment=None):
        date = self.date
        comm_type = self.comm_type
        type_id = self.type_id
        filename = utils.generate_filename(type_id, comm_type, date)
        html_email_data = {
            'type_id': type_id,
            'filename': filename,
            'html_template_type': comm_type,
            'subject': self.subject,
            'comment': self.comment
        }
        serializer_2 = serializers.HTMLEmailSerializer(data=html_email_data)
        if serializer_2.is_valid(raise_exception=True):
            if sr_data is None:
                serializer_add = self.serializer_add(data=sr_data_add, many=True)
                if serializer_add.is_valid(raise_exception=True):
                    serializer_data = {**serializer_add.data, **serializer_2.data}
            elif sr_data_add is None:
                serializer = self.serializer(data=sr_data)
                if serializer.is_valid(raise_exception=True):
                    serializer_data = {**serializer.data, **serializer_2.data}
            elif sr_data is None and sr_data_add is None:
                serializer_data = serializer_2
            else:
                serializer = self.serializer(data=sr_data)
                serializer_add = self.serializer_add(data=sr_data_add, many=True)
                if serializer.is_valid(raise_exception=True) and serializer_add.is_valid(raise_exception=True):
                    serializer_data = {**serializer.data, **serializer_add.data, **serializer_2.data}
            r = requests.post(url='http://host.docker.internal:3000/html-email', json=serializer_data)
            r_message = r.json()['message']
            if r_message == 'render_successful':
                html_file = self.return_email(filename)
                if True:
                    self.preform_send_email(html_file, attachment)
                    if True:
                        if self.serializer_comm_history is not None:
                            self.save_to_comm_history(comm_method='email', comm_recipient='self.email')
                        return True
            else:
                return False

    def send_sms(self):
        self.perform_send_sms()
        if self.comm_type != 'OTP':
            self.save_to_comm_history(comm_method='SMS', comm_recipient=self.mobile_no)

class UpdateStatusViewSetMixin(CommunicationViewSetObjectMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_status(self, current_status_id, comm_method):
        sr_data = {
            'current_status_id': current_status_id,
            'current_status_date': self.date,
            'current_status_comment': self.comment
        }
        sr_data_add = {
            f'{self.obj_type}_id': self.type_id
        } + sr_data
        serializer = self.serializer(instance=self.instance, data=sr_data, partial=True)
        if comm_method == 'SMS':
            self.send_sms()
        if comm_method == 'email':
            self.send_email(sr_data=None, data_add=sr_data_add)
        if comm_method == 'SMS, email':
            self.send_sms()
            self.send_email(sr_data=None, data_add=sr_data_add)
        serializer.save()

class SendEmailConfViewSetMixin(CommunicationViewSetObjectMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render_conf(self, sr_data):
        if self.obj_type == 'order':
            sr_data_add = {}
            OrderItems.objects.filter(order_id=self.type_id).values().append(data_add)
            return self.send_email(sr_data=sr_data, sr_data_add=sr_data_add)
        else:
            return self.send_email(sr_data=sr_data, sr_data_add=None)

class SendOtpViewSetMixin(CommunicationViewSetObjectMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_otp(self, length=6):
        characters = string.digits
        otp = ''.join(random.choice(characters) for _ in range(length))
        return otp

    def send_otp(self, sr_data, comm_method):
        if comm_method == 'SMS':
            if self.send_sms():
                return True
        if comm_method == 'email':
            if self.send_email(sr_data=sr_data, sr_data_add=None):
                return True
        else:
            return False
        # if comm_method == 'SMS, email':
        #     self.send_sms()
        #     self.send_email(sr_data=sr_data, sr_data_add=None)