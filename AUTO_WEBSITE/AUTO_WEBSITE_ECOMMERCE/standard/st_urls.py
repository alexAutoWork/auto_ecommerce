from rest_framework import routers
from . import st_views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'products', st_views.ProductsViewSet, 'products')
router.register(r'brands', st_views.BrandsViewSet, 'brands')
router.register(r'categories', st_views.CategoriesViewSet, 'categories')
router.register(r'cities', st_views.CitiesViewSet, 'cities')

st_urls = router.urls

urlpatterns = [
    path('', include(st_urls)),
    path('test', st_views.TestView.as_view(), name='test')
]