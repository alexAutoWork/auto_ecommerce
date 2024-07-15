from rest_framework import viewsets, status, views, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from . import utils, serializers
from django.conf import settings

class UploadView(views.APIView):

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = serializers.FileSerializer(data=request.data, many=True)
        if serializer.is_valid(raise_exception=True):
            try:
                file = serializer.data['file']
                user_type = serializer.data['user_type']
                if user_type == 'user':
                    user_prefix = f'user_id_{user.user_id}'
                if user_type == 'admin':
                    user_prefix = user_type
                datetime = utils.return_date_and_time()
                instance_type = serializer.data['instance_type']
                instance_id = serializer.data.get('instance_id', None)
                keywords = {
                    'user': user_prefix,
                    'instance_type': instance_type
                }
                file_type = serializer.data['file_type']
                if instance_id is not None:
                    folder = f'{instance_type}/{instance_id}/'
                else:
                    folder = f'temp/'
                folder = f'{folder}{file_type}/'
                filename = utils.generate_filename(datetime=datetime, **keywords)
                path = f'{folder}{filename}'
                request.session[filename] = {'path': path, 'is_active': True}
                default_storage.save(path, ContentFile(file.read()))
                return Response({'message': 'File Uploaded Successfully!', 'filename': filename}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        filename = request.query_params.get('filename', None)
        if filename is not None:
            filename = request.session['filename']
            path = filename.get('path', None)
            is_active = filename.get('is_active', False)
            if (path is not None) and (is_active is True):
                default_storage.exists(path)
                if True:
                    default_storage.delete(path)
                    request.session[filename] = {'path': path, 'is_active': False}
                    return Response({'message': 'File Deleted Successfully!'}, status=status.HTTP_200_OK)

class Test(views.APIView):
    def post(self, request):
        try:
            print(settings.EMAIL_HOST_USER)
            print(settings.EMAIL_HOST_PASSWORD)
            subject = 'subject'
            message = 'test message'
            from_email = 'noreply@autolectronix.co.za'
            recipient_list = [request.data.get('email', None)]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            return Response({'message': 'success!!'}, status=status.HTTP_200_OK)
        except Exception:
            return Exception