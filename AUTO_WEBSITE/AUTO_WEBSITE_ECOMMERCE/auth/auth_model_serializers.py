# Serializers Model File Only Accessible with Authorization

from rest_framework import serializers
from . import auth_models
from ..standard.st_model_serializers import ProductsSerializer, StatusesSerializer
from ..reg import reg_models
from ..reg.reg_model_serializers import UserAddressesSerializer
from ..standard import st_models, st_model_serializers
from .. import mixins, serializer_fields, serializers as custom_serializers

# Shopping Cart Model Serializers

class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.ShoppingCart
        fields = '__all__'

class ShoppingCartItemsSerializer(custom_serializers.NestedSerializer):
    nested_fields = {'product_config_id': st_model_serializers.ProductConfigSerializer}
    class Meta:
        model = auth_models.ShoppingCartItems
        fields = '__all__'

# Order Model Serializers

class OrdersSerializer(custom_serializers.NestedSerializer):
    nested_fields = {'shipping_address_id': UserAddressesSerializer}
    shipping_method_id = serializer_fields.SerializerOrPkField(queryset=st_models.ShippingMethods.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'shipping_method_value'})
    current_status_id = serializer_fields.SerializerOrPkField(queryset=st_models.Statuses.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'status_value'})
    # shipping_address_id = UserAddressesSerializer(read_only=True)
    # shipping_method_id = serializers.SlugRelatedField(read_only=True, slug_field='shipping_method_value')
    # current_status_id = serializers.SlugRelatedField(read_only=True, slug_field='status_value')
    
    class Meta:
        model = auth_models.Orders
        fields = '__all__'

class OrderExUnitImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.OrderItems
        fields = ['order_ex_unit_filename']

class OrderItemsSerializer(custom_serializers.NestedSerializer):
    nested_fields = {'sku_no': st_model_serializers.ProductStocksSerializer}
    # sku_no = serializer_fields.SerializerOrPkField(queryset=st_models.ProductStocks.objects.all(), alt_field=st_model_serializers.ProductStocksSerializer)
    # sku_no = st_model_serializers.ProductConfigSerializer(read_only=True)
    class Meta:
        model = auth_models.OrderItems
        fields = '__all__'

class OrderHistorySerializer(serializers.ModelSerializer):
    status_id = serializers.SlugRelatedField(read_only=True, slug_field='status_value')
    # status_id = serializers.SlugRelatedField(read_only=True, slug_field='status_value')

    class Meta:
        model = auth_models.OrderHistory
        fields = '__all__'

class OrderCommunicationHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.OrderCommunicationHistory
        fields = '__all__'

# Invoice Model Serializers

class InvoicesSerializer(custom_serializers.NestedSerializer):
    nested_fields = {'order_id': OrdersSerializer}
    # order_id = serializer_fields.SerializerOrPkField(queryset=auth_models.Orders.objects.all(), alt_field=OrdersSerializer)

    class Meta:
        model = auth_models.Invoices
        fields = '__all__'
        depth = 1

class InvoiceItemsSerializer(custom_serializers.NestedSerializer):
    nested_fields = {'order_item_id': OrderItemsSerializer}
    # order_item_id = serializer_fields.SerializerOrPkField(queryset=auth_models.OrderItems.objects.all(), alt_field=OrderItemsSerializer)
    class Meta:
        model = auth_models.InvoiceItems
        fields = '__all__'

# Repair Model Serializer

class RepairsSerializer(custom_serializers.NestedSerializer):
    nested_fields = {
        'product_id': st_model_serializers.ProductsSerializer,
        'shipping_address_id': UserAddressesSerializer
    }
    # product_id = serializer_fields.SerializerOrPkField(queryset=st_models.Products.objects.all(), alt_field=st_model_serializers.ProductsSerializer)
    shipping_method_id = serializer_fields.SerializerOrPkField(queryset=st_models.ShippingMethods.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'shipping_method_value'})
    # shipping_address_id = serializer_fields.SerializerOrPkField(queryset=reg_models.UserAddresses.objects.all(), alt_field=UserAddressesSerializer)
    current_status_id = serializer_fields.SerializerOrPkField(queryset=st_models.Statuses.objects.all(), alt_field=serializers.SlugRelatedField, alt_field_params={'slug_field': 'status_value'})
    # product_id = ProductsSerializer(read_only=True)
    # current_status_id = serializers.SlugRelatedField(read_only=True, slug_field='status_value')
    class Meta:
        model = auth_models.Repairs
        fields = '__all__'
        depth = 1

class RepairHistorySerializer(serializers.ModelSerializer):
    status_id = serializers.SlugRelatedField(read_only=True, slug_field='status_value')
    class Meta:
        model = auth_models.RepairHistory
        fields = '__all__'

class RepairCommunicationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.RepairCommunicationHistory
        fields = '__all__'

# Return Model Serializers

class ReturnsSerializer(custom_serializers.NestedSerializer):
    nested_fields = {'order_item_id': OrderItemsSerializer}
    # order_item_id = serializer_fields.SerializerOrPkField(queryset=auth_models.OrderItems.objects.all(), alt_field=OrderItemsSerializer)
    class Meta:
        model = auth_models.Returns
        fields = '__all__'

class ReturnHistorySerializer(serializers.ModelSerializer):
    status_id = serializers.SlugRelatedField(read_only=True, slug_field='status_value')
    class Meta:
        model = auth_models.ReturnHistory
        fields = '__all__'
        depth = 1

class ReturnCommunicationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.ReturnCommunicationHistory
        fields = '__all__'
