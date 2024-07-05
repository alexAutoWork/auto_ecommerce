from rest_framework import viewsets, views, status
from django_filters import rest_framework as custom_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from . import st_models, st_serializers, st_model_serializers
from django.db.models.functions import Concat
import requests, json
from .. import utils, permissions
from ..admin import admin_permissions
from django.shortcuts import get_object_or_404
from decimal import Decimal as dec
from django.db.models import Prefetch, Q
import functools, operator
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

class ProductsViewSet(viewsets.ViewSet):
    permission_classes = [admin_permissions.AdminObjectType1Permission|permissions.BaseReadPermission]
    default = {'is_active': True, 'stock_available__gte': 1}

    parent_serializer = st_model_serializers.ProductsSerializer
    parent_model = st_models.Products

    custom_actions = ['get_shipping_rate_on_change']

    def standard_mini_product_dict(self, item):
        '''
        make small dict out of product queryset
        '''
        mini_dict = {}
        if hasattr(item, 'city_id'):
            city_dict = {
                'product_id': item.product_id.pk,
                'city_id': item.city_id.pk,
                'base_charge': dec(item.base_charge)
            }
            item = item.product_id
            mini_dict['shipping_rate'] = city_dict
        product_dict = {
            'product_id': item.pk,
            'name': item.name,
            'brand_id': item.brand_id.pk,
            'category_id': item.category_id.pk,
            'is_repairable': item.is_repairable,
            'product_img_thumb': item.product_img_thumb
        }
        mini_dict['product'] = product_dict
        return mini_dict

    def filter_kwargs(self, query_params_list, **kwargs):
        '''
        make filter kwargs using Q obj
        '''
        has_city_id = kwargs.get('has_city_id', False)
        filter_list = Q()
        if query_params_list is not None:
            for item in query_params_list:
                for key, value in item.items():
                    if has_city_id:
                        key = f'product_id__{key}'
                    query_params = value.split(',')
                    for item in query_params:
                        filter_list.add(Q(**{key: item}), Q.OR)
        for key, value in self.default.items():
            if has_city_id:
                key = f'product_id__{key}'
            filter_list.add(Q(**{key: value}), Q.AND)
        return filter_list

    def list(self, request):
        '''
        list product items using the following filters (if passed):
        - city_id
        - brand_id
        - category_id
        - sort by
        '''
        city_id = request.query_params.get('city_id', None)
        # request city_id as query param
        if city_id is not None:
            request.session['city_id'] = city_id
        else:
            city_id = request.session.get('city_id', None)
        # save to session if given, if not, try to fetch from sessions
        if city_id is not None:
            has_city_id = True
            prefetch_query = Prefetch('product_id', queryset=st_models.Products.objects.all())
            queryset = st_models.BaseShippingRates.objects.prefetch_related(prefetch_query).all()
            queryset = queryset.filter(city_id=city_id)
            print(queryset)
            # queryset = cache.get(f'products_city_id')
            # if queryset is None:
            #     prefetch_query = Prefetch('product_id', queryset=st_models.Products.objects.all())
            #     queryset = st_models.BaseShippingRates.objects.prefetch_related(prefetch_query).all()
                # cache.set('products_city_id', queryset)
            # queryset = queryset.filter(city_id=city_id)
        else:
            has_city_id = False
            queryset = cache.get('products')
            if queryset is None:
                queryset = st_models.Products.objects.all()
                cache.set('products', queryset)
            print(queryset)
        # get queryset from cache, otherwise run db query and save to cache
        data = []
        filter_list = []
        sort_by = request.query_params.get('sort', None)
        filter_brand = request.query_params.get('filter_brand', None)
        if filter_brand is not None:
            filter_list.append({'brand_id': filter_brand})
        filter_category = request.query_params.get('filter_category', None)
        if filter_category is not None:
            filter_list.append({'category_id': filter_category})
        print(filter_list)

        if filter_list != 0:
            filter_list = self.filter_kwargs(filter_list, has_city_id=has_city_id)
        if sort_by is None:
            sort_by = 'name'
        if has_city_id:
            sort_by = f'product_id__{sort_by}'
        queryset = queryset.filter(filter_list).order_by(sort_by)
        print(filter_list)

        # filter using prev queryset
        for item in queryset:
            data.append(self.standard_mini_product_dict(item))
        print(queryset)
        serializer = st_serializers.ProductShippingRateComboSerializer(data=data, many=True)
        # make dict and run queryset through serializer
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_models(self, request, **kwargs):
        product_id = kwargs.get('product_id', None)
        if product_id is not None:
            pk_field = {'product_id': product_id}
            cache_name = utils.create_cache_name(model='models', pk_fields=pk_field)
            models = cache.get_or_set(cache_name, st_models.ProductModels.objects.filter(**pk_field))
            serializer = st_model_serializers.ProductModelsSerializer(models, many=True, context={'request': request})
            return {'product_models': serializer.data}
            # if serializer.is_valid(raise_exception=True):
            #     return serializer.data

    def get_prices(self, request, **kwargs):
        product_id = kwargs.get('product_id', None)
        if product_id is not None:
            pk_field = {'product_id': product_id}
            configs = st_models.ProductConfig.objects.filter(product_id=product_id)
            # cache_name = utils.create_cache_name(model='configs', pk_fields=pk_field)
            # configs = cache.get_or_set(cache_name, st_models.ProductConfig.objects.filter(product_id=product_id))
            serializer = st_model_serializers.ProductConfigSerializer(configs, context={'request': request}, many=True)
            return {'product_prices': serializer.data}
            # if serializer.is_valid(raise_exception=True):
            #     return serializer.data
    
    def get_shipping_rate(self, city_id, product_id):
        filter_fields = {'product_id': product_id, 'city_id': city_id}
        cache_name = utils.create_cache_name(model='configs', pk_fields=filter_fields)
        shipping_rate = cache.get(cache_name)
        if shipping_rate is None:
            shipping_rate = st_models.BaseShippingRates.objects.select_related('city_id').filter(**filter_fields).first()
            cache.set(cache_name, shipping_rate)
        data = {
            'city_value': shipping_rate.city_id.city_value,
            'base_charge': shipping_rate.base_charge
        }
        serializer = st_serializers.SimpleShippingRateComboSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return serializer.data

    def get_other_details(self, model, model_name, pk_field, serializer_model):
        queryset = model.objects.get(pk=pk_field)
        serializer = serializer_model(queryset)
        return {f'{model_name}': serializer.data}

    def retrieve(self, request, pk=None):
        pk_field = {'product_id': pk}
        cache_name = utils.create_cache_name(model='products', pk_fields=pk_field)
        product = cache.get(cache_name)
        if product is None:
            try:
                product = st_models.Products.objects.select_related('brand_id', 'category_id').filter(**pk_field, **self.default).first()
                cache.set(cache_name, product)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        product_id = product.pk
        brand_id = product.brand_id
        category_id = product.category_id
        serializer = st_model_serializers.ProductsSerializer(product, context={'request': request})
        data = {}
        data['product_details'] = serializer.data
        model_serializer = self.get_models(request, product_id=product_id)
        price_serializer = self.get_prices(request, product_id=product_id)
        city_id = request.session.get('city_id')
        if city_id is not None:
            shipping_rate = self.get_shipping_rate(city_id=city_id, product_id=product_id)
            data['product_shipping_rate'] = shipping_rate
        data.update(model_serializer)
        data.update(price_serializer)
        return Response(data, status=status.HTTP_202_ACCEPTED)
        
    @action(detail=True)
    def get_shipping_rate_on_change(self, request, pk=None):
        city_id = request.query_params['city_id']
        request.session['city_id'] = city_id
        rate = self.get_shipping_rate(city_id, pk)
        return Response(rate, status=status.HTTP_202_ACCEPTED)

class BrandsViewSet(viewsets.ViewSet):
    permission_classes = [admin_permissions.AdminObjectType1Permission|permissions.BaseReadPermission]

    parent_serializer = st_model_serializers.BrandsSerializer
    parent_model = st_models.Brands

    def list(self, request):
        queryset = cache.get('brands', self.parent_model.objects.all())
        serializer = self.parent_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoriesViewSet(viewsets.ViewSet):
    permission_classes = [admin_permissions.AdminObjectType1Permission|permissions.BaseReadPermission]

    parent_serializer = st_model_serializers.CategoriesSerializer
    parent_model = st_models.Categories

    def list(self, request):
        queryset = cache.get_or_set('categories', self.parent_model.objects.all())
        serializer = self.parent_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CitiesViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.BaseReadPermission]
    queryset = st_models.Cities.objects.all()
    serializer_class = st_model_serializers.CitiesSerializer

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