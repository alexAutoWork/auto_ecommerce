from rest_framework import serializers
from phonenumber_field import serializerfields
from ..reg import reg_model_serializers
from . import auth_model_serializers

class CheckoutTotalDimSerializer(serializers.Serializer):
    total_dim_l = serializers.DecimalField(max_digits=12, decimal_places=4)
    total_dim_h = serializers.DecimalField(max_digits=12, decimal_places=4)
    total_dim_w = serializers.DecimalField(max_digits=12, decimal_places=4)
    total_weight = serializers.DecimalField(max_digits=12, decimal_places=4)

class CheckoutTotalSerializer(serializers.Serializer):
    subtotal_excl = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_quantity = serializers.IntegerField()
    shipping = serializers.DecimalField(max_digits=12, decimal_places=2)
    subtotal_incl = serializers.DecimalField(max_digits=12, decimal_places=2)
    vat = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)

class CheckoutHasExchangeUnitSerializer(serializers.Serializer):
    shopping_cart_item_id = serializers.IntegerField()
    product_id = serializers.CharField()
    product_name = serializers.CharField()
    contains_exchange_unit = serializers.BooleanField()

class InvoiceItemRenderSerializer(serializers.Serializer):
    invoice_item_code = serializers.CharField()
    invoice_item_sku_no = serializers.CharField()
    invoice_item_name = serializers.CharField()
    invoice_item_variation = serializers.CharField()
    invoice_item_excl = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_item_vat = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_item_incl = serializers.DecimalField(max_digits=12, decimal_places=2)

class InvoiceRenderSerializer(serializers.Serializer):
    filename = serializers.CharField()
    invoice_id = serializers.CharField()
    order_id = serializers.CharField()
    invoice_date = serializers.DateField()
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    customer_mobile = serializerfields.PhoneNumberField()
    customer_company = serializers.CharField()
    customer_company_reg_no = serializers.CharField()
    customer_vat_no = serializers.CharField()
    invoice_shipping = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_subtotal_excl = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_tax = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_subtotal_incl = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_items = InvoiceItemRenderSerializer(many=True)

class ShoppingCartItemsSerializerEx(auth_model_serializers.ShoppingCartItemsSerializer):
    shopping_cart_item_id = serializers.IntegerField(required=False, allow_null=True)
    product_id = serializers.CharField()
    product_name = serializers.CharField()
    product_img_thumb = serializers.CharField()
    product_weight_type = serializers.CharField()
    product_weight = serializers.DecimalField(max_digits=12, decimal_places=2)
    product_dim_h = serializers.DecimalField(max_digits=12, decimal_places=2)
    product_dim_l = serializers.DecimalField(max_digits=12, decimal_places=2)
    product_dim_w = serializers.DecimalField(max_digits=12, decimal_places=2)
    variation_id = serializers.IntegerField()
    variation_value = serializers.CharField()
    shopping_cart_id = None

class OrderItemsSerializerEx(auth_model_serializers.OrderItemsSerializer):
    product_id = serializers.CharField()
    product_name = serializers.CharField()
    product_img_thumb = serializers.CharField()
    variation_id = serializers.IntegerField()
    variation_value = serializers.CharField()

class ReturnsSerializerEx(auth_model_serializers.ReturnsSerializer):
    current_status_value = serializers.CharField()
    order_date = serializers.DateField()
    sku_no = serializers.CharField()
    product_id = serializers.CharField()
    product_name = serializers.CharField()
    product_img_thumb = serializers.CharField()
    product_config_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    variation_id = serializers.IntegerField()
    variation_value = serializers.CharField()
    class Meta:
        depth = 0