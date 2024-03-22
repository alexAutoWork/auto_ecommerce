from rest_framework import viewsets, views, status
from django_filters import rest_framework as custom_filters
from rest_framework.response import Response
from rest_framework import filters
from . import st_models, st_serializers
from django.db.models.functions import Concat
import requests, json
from .. import utils

class ProductsFilter(custom_filters.FilterSet):
    variation = custom_filters.CharFilter(field_name='products_id', method='get_product_filters')
    brand = custom_filters.CharFilter(field_name='brands_id', method='get_product_filters')
    category = custom_filters.CharFilter(field_name='categories_id', method='get_product_filters')

    def get_product_variations(self, value):
        products_id = st_models.ProductConfig.objects.filter(variation_id=value).values('products_id')
        return self.objects.filter(products_id=products_id)

    def get_product_filters(self, field_name, value):
        lookup = field_name + '__iexact'
        if field_name == 'variation_id':
            return get_product_variations(value)
        else:
            return self.objects.filter(**{lookup: value})

    class Meta:
        model = st_models.Products
        fields = ['products_id', 'brands_id', 'categories_id']

class StandardProductsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = st_serializers.ProductsSerializer
    filter_backends = [filters.OrderingFilter, custom_filters.DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_class = ProductsFilter()

    def get_queryset(self):
        city_id = self.request.data['city_id']
        baseshippingrate = st_models.BaseShippingRates.objects.filter(city_id=city_id).order_by('products_id').values('city_id', 'products_id', 'base_charge')
        products = st_models.Products.objects.order_by('products_id').all()
        return Concat(baseshippingrate, products).get()

class ProductModelsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = st_serializers.ProductModelsSerializer()

    def get_queryset(self):
        products_id = self.request.data['products_id']
        return st_models.ProductModels.objects.filter(products_id=products_id)

class BrandsViewSet(viewsets.ModelViewSet):
    queryset = st_models.Brands.objects.all()
    serializer_class = st_serializers.BrandsSerializer

class CategoriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = st_models.Categories.objects.all()
    serializer_class = st_serializers.CategoriesSerializer

class TestView(views.APIView):
    def post(self, request):
        is_send = request.data.get('is_send')
        if is_send == 'not sent':
            r = requests.post(url='http://172.19.0.3:3000/test', json={'message': 'sent'})
            data = r.json()
            is_send_fe = data['is_send']
            if is_send_fe == 'sent':
                return Response(data={'message': 'entire process successful!'}, status=status.HTTP_200_OK)
        # if is_send == 'sent':
        #     return Response(data={'message': 'entire process successful!'}, status=status.HTTP_200_OK)
        # return Response(data={'message': 'unsuccessful'}, status=status.HTTP_204_NO_CONTENT)
        # print(r.text)
        # return Response(data={'message': 'entire process successful!'}, status=status.HTTP_200_OK)
        # data = json.loads(r.json())
        # is_success = data.get('is_success')
        # if is_success:
        #     return Response(data={'message': 'entire process successful!'}, status=status.HTTP_200_OK)
        # else:
        #     return Response(data={'message': 'unsuccessful'}, status=status.HTTP_204_NO_CONTENT)