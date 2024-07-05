from rest_framework import viewsets, views, status, permissions
from . import admin_permissions
from ..standard import st_models, st_model_serializers
from django.core.cache import cache

class ProductStocksViewSet(viewsets.ViewSet):
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    
    # queryset = st_models.ProductStocks.objects.all()
    # serializer_class = st_model_serializers.ProductStocksSerializer

    parent_serializer = st_model_serializers.ProductStocksSerializer
    parent_model = st_models.ProductStocks

    def list(self, request):
        queryset = cache.get_or_set('product_stocks', parent_model.objects.all())
        serializer = parent_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductModelsViewSet(viewsets.ViewSet):
    permission_classes = [admin_permissions.AdminObjectType1Permission]

    parent_serializer = st_model_serializers.ProductModelsSerializer
    parent_model = st_models.ProductModels

    def list(self, request):
        queryset = cache.get_or_set('product_models', parent_model.objects.all())
        serializer = parent_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)