from rest_framework import routers
from . import reg_views
from django.urls import path, include

router1 = routers.DefaultRouter()
router1.register(r'details', reg_views.UserDetailsViewSet, 'user-details')
router1.register(r'addresses', reg_views.UserAddressViewSet, 'user-addresses')
router2 = routers.DefaultRouter()
router2.register(r'', reg_views.VerifyViewSet, 'verify')
router2.register(r'forgot', reg_views.SensViewSet, 'forgot')

user_urls = router1.urls
reg_urls = router2.urls

urlpatterns = [
    path('login/', reg_views.LoginView.as_view(), name='login'),
    path('register/', reg_views.RegisterView.as_view(), name='register'),
    path('logout/', reg_views.LogoutView.as_view(), name='logout'),
    path('user/', include(user_urls)),
    path('', include(reg_urls))
]