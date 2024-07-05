from rest_framework import routers
from .admin_mixins import UniversalAdminMixin
from django.urls import path, include

def startup():
    admin = UniversalAdminMixin()
    custom_actions_list = admin.admin_mixin_mro()
    return custom_actions_list

custom_actions = startup()

from . import admin_views

router = routers.DefaultRouter()
router.register(r'products', admin_views.ProductAdminViewSet, 'products')

router._urls = [
    r for r in router.urls
    if not any(r.name.endswith(bad) for bad in custom_actions)
]

admin_urls = router._urls

urlpatterns = [
    path('admin/', include(admin_urls))
]