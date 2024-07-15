from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .auth.auth_urls import urlpatterns as auth_urls
from .standard.st_urls import urlpatterns as st_urls
from .reg.reg_urls import urlpatterns as reg_urls
from .admin.admin_urls import urlpatterns as admin_urls
from . import mixins as custom_mixins
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(reg_urls)),
    path('', include(auth_urls)),
    path('', include(st_urls)),
    path('', include(admin_urls)),
    path('upload', views.UploadView.as_view(), name='upload'),
    path('test2', views.Test.as_view(), name='test2')
]