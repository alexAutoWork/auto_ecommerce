from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .auth.auth_urls import urlpatterns as auth_urls
from .standard.st_urls import urlpatterns as st_urls
from .reg.reg_urls import urlpatterns as reg_urls
from . import mixins as custom_mixins

router = routers.DefaultRouter()
router.register(r'send-comm', custom_mixins.CommunicationViewSetObjectMixin, 'send-comm')

ot_urls = router.urls

urlpatterns = [
    path('', include(reg_urls)),
    path('', include(auth_urls)),
    path('', include(st_urls)),
    path('', include(ot_urls))
]