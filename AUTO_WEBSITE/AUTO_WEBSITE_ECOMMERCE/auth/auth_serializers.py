from rest_framework import serializers
from phonenumber_field import serializerfields

class CheckoutTotalDimSerializer(serializers.Serializer):
    total_dim_l = serializers.DecimalField(max_digits=12, decimal_places=4)
    total_dim_h = serializers.DecimalField(max_digits=12, decimal_places=4)
    total_dim_w = serializers.DecimalField(max_digits=12, decimal_places=4)
    total_weight = serializers.DecimalField(max_digits=12, decimal_places=4)

class CheckoutTotalSerializer(serializers.Serializer):
    total_quantity = serializers.IntegerField()
    shipping = serializers.DecimalField(max_digits=12, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    vat = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)

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
    customer_reg_no = serializers.CharField()
    customer_vat_no = serializers.CharField()
    invoice_shipping = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_excl = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_vat = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_items = InvoiceItemRenderSerializer(many=True)
    
# class CheckoutPayfastSerializer(serializers.Serializer):
