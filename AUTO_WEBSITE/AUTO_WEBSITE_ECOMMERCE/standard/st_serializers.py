from rest_framework import serializers
from rest_framework import fields
from . import st_models

# Product Model Serializers

class BrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Brands
        fields = ['brands_id', 'value']

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Categories
        fields = ['categories_id', 'value']

class VariationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Variations
        fields = ['variation_id', 'value']

class ProductsSerializer(serializers.ModelSerializer):

    class Meta:
        model = st_models.Products
        fields = ['products_id', 'name', 'weight', 'dimension_h', 'dimension_l', 'dimension_w', 'brands_id', 'categories_id', 'product_img', 'product_img_thumb', 'warranty', 'is_repairable', 'stock_available', 'is_active']

class ProductConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = st_models.ProductConfig
        fields = ['product_config_id', 'products_id', 'variation_id', 'price', 'is_synced', 'sage_id', 'sage_item_id']

class ProductModelsSerializer(serializers.ModelSerializer):

    class Meta:
        model = st_models.ProductModels
        fields = ['model_number', 'products_id']

class ProductStockSerializer(serializers.ModelSerializer):

    class Meta:
        model = st_models.ProductStock
        fields = ['sku_no', 'product_config_id', 'is_purchased']

# Shipping Model Serializers

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.ShippingMethod
        fields = ['shipping_method_id', 'value']

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Cities
        fields = ['city_id', 'city', 'ram_address_1', 'ram_address_2', 'region', 'postal_code']

class BaseShippingRatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = st_models.BaseShippingRates
        fields = ['shipping_rate_id', 'city_id', 'products_id', 'base_charge']

# Status Model Serializer

class StatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = st_models.Statuses
        fields = ['id_status', 'status_type', 'value', 'is_active']

