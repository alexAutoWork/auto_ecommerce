from rest_framework import serializers
from rest_framework import fields
from . import st_models
from .. import serializers as custom_serializers, serializer_fields

# Product Model Serializers

class BrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Brands
        fields = '__all__'

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Categories
        fields = '__all__'

class VariationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Variations
        fields = '__all__'

class BaseShippingRatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = st_models.BaseShippingRates
        fields = '__all__'

class ProductsSerializer(serializers.ModelSerializer):
    brand_id = serializer_fields.SerializerOrPkField(queryset=st_models.Brands.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'brand_value'})
    category_id = serializer_fields.SerializerOrPkField(queryset=st_models.Categories.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'category_value'})
    class Meta:
        model = st_models.Products
        fields = '__all__'

class ProductConfigSerializer(custom_serializers.NestedSerializer):
    nested_fields = {'product_id': ProductsSerializer}
    # product_id = serializer_fields.SerializerOrPkField(queryset=st_models.Products.objects.all(), alt_field=ProductsSerializer, is_serializer=True)
    variation_id = serializer_fields.SerializerOrPkField(queryset=st_models.Variations.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'variation_value'})
    # product_id = ProductsSerializer(read_only=True)
    # variation_id = VariationsSerializer(read_only=True)
    class Meta:
        model = st_models.ProductConfig
        fields = '__all__'

class ProductModelsSerializer(serializers.ModelSerializer):
    product_id = serializer_fields.SerializerOrPkField(queryset=st_models.Products.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'name'})
    class Meta:
        model = st_models.ProductModels
        fields ='__all__'

class ProductStocksSerializer(custom_serializers.NestedSerializer):
    nested_fields = {'product_config_id': ProductConfigSerializer}
    # product_config_id = serializer_fields.SerializerOrPkField(queryset=st_models.ProductConfig.objects.all(), alt_field=ProductConfigSerializer, is_serializer=True)
    current_status_id = serializer_fields.SerializerOrPkField(queryset=st_models.Statuses.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'status_value'})
    class Meta:
        model = st_models.ProductStocks
        fields = '__all__'

# Shipping Model Serializers

class ShippingMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.ShippingMethods
        fields = '__all__'

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Cities
        fields = '__all__'
# Status Model Serializer

class StatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Statuses
        fields = '__all__'