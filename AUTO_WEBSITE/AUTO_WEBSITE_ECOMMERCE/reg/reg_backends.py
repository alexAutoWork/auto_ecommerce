from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        UserModel = get_user_model()
        try:
            email = kwargs.get('email', None)
            mobile_no = kwargs.get('mobile_no', None)
            if email is not None and mobile_no is not None:
                user = UserModel.objects.get(email=email, mobile_no=mobile_no)
            else:
                if email is None:
                    user = UserModel.objects.get(mobile_no=mobile_no)
                if mobile_no is None:
                    user = UserModel.objects.get(email=email)
            if check_password(kwargs.get('password', None), user.password):
                return user
        except UserModel.DoesNotExist:
            return None
        return None
