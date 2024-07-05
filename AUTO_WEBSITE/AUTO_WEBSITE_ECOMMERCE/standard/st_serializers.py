from rest_framework import serializers
from rest_framework import fields
from . import st_model_serializers

class PartialProductSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    name = serializers.CharField()
    category_id = serializers.CharField()
    brand_id = serializers.CharField()
    is_repairable = serializers.BooleanField()
    product_img_thumb = serializers.CharField()

# NOT model serializer
class ProductShippingRateComboSerializer(serializers.Serializer):
    product = PartialProductSerializer()
    shipping_rate = st_model_serializers.BaseShippingRatesSerializer(required=False)

class SimpleShippingRateComboSerializer(serializers.Serializer):
    city_value = serializers.CharField()
    base_charge = serializers.DecimalField(max_digits=12, decimal_places=2)