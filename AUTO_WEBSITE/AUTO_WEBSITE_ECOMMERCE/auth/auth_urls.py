from rest_framework import routers
from . import auth_views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'cart', auth_views.ShoppingCartViewSet, 'cart')
router.register(r'orders', auth_views.OrdersViewSet, 'orders')
router.register(r'invoices', auth_views.InvoicesViewSet, 'invoices')
router.register(r'checkout', auth_views.Checkout, 'checkout')

checkout_custom_actions = ['checkout-render-order-conf', 'checkout-render-repair-conf', 'checkout-retrieve-items']

router._urls = [
    r for r in router.urls
    if not any(r.name.endswith(bad) for bad in checkout_custom_actions)
]

auth_urls = router._urls

urlpatterns = [
    path('auth/', include(auth_urls))
]