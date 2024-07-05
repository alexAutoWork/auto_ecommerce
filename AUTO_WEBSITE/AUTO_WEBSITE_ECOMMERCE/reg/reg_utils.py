from rest_framework.response import Response
from django.contrib.auth import logout as dj_logout
from rest_framework import status

def logout(request):
    dj_logout(request)
    response = Response()
    response.delete_cookie('access_token')
    response.status_code = status.HTTP_202_ACCEPTED
    return response