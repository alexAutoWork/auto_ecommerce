from rest_framework import routers
from . import reg_views
from django.urls import path, include

router = routers.DefaultRouter()

urlpatterns = [
    path('login', reg_views.LoginView.as_view(), name='login'),
    path('register', reg_views.RegisterView.as_view(), name='register'),
    path('send-otp', reg_views.SendOtp.as_view(), name='send_otp'),
    path('verify-otp', reg_views.VerifyOTP.as_view(), name='verify_otp')
]