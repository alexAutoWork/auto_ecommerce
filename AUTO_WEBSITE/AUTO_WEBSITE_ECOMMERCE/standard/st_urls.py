from rest_framework import routers
from . import st_views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'products', st_views.StandardProductsViewSet, 'products')
router.register(r'product-models', st_views.ProductModelsViewSet, 'product-models')
router.register(r'brands', st_views.BrandsViewSet, 'brands')
router.register(r'categories', st_views.CategoriesViewSet, 'categories')

st_urls = router.urls

urlpatterns = [
    path('', include(st_urls)),
    path('test', st_views.TestView.as_view(), name='test')
]