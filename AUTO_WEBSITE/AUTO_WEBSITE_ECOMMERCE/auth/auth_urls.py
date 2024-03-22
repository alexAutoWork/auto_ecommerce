from rest_framework import routers
from . import auth_views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'cart', auth_views.ShoppingCartViewSet, 'cart')
router.register(r'cart-items', auth_views.ShoppingCartItemsViewSet, 'cart-items')
router.register(r'orders', auth_views.OrdersViewSet, 'orders')
router.register(r'order-items', auth_views.OrderItemsViewSet, 'order-items')
router.register(r'order-history', auth_views.OrderHistoryViewSet, 'order-history')
router.register(r'invoices', auth_views.InvoiceViewSet, 'invoices')
router.register(r'invoice-items', auth_views.InvoiceItemsViewSet, 'invoice-items')
router.register(r'returns', auth_views.ReturnsViewSet, 'returns')
router.register(r'return-history', auth_views.ReturnHistoryViewSet, 'return-history')
router.register(r'repairs', auth_views.RepairsViewSet, 'repairs')
router.register(r'repair-history', auth_views.RepairHistoryViewSet, 'repair-history')

auth_urls = router.urls

urlpatterns = [
    path('checkout', auth_views.Checkout.as_view()),
    path('auth/', include(auth_urls))
]