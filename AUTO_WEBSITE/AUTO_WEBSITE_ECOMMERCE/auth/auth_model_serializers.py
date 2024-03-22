# Serializers Model File Only Accessible with Authorization

from rest_framework import serializers
from . import auth_models
from ..standard.st_serializers import ProductsSerializer, StatusesSerializer
from ..reg.reg_model_serializers import UserAddressSerializer
from ..standard import st_models

# Shopping Cart Model Serializers

class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.ShoppingCart
        fields = ['shopping_cart_id', 'user_id', 'subtotal', 'vat', 'total']

class ShoppingCartItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.ShoppingCartItems
        fields = ['shopping_cart_items_id', 'shopping_cart_id', 'product_config_id', 'quantity', 'total_price']

# Order Model Serializers

class OrdersSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.Orders
        fields = ['order_id', 'user_id', 'order_date', 'shipping_address_id', 'shipping_method_id', 'shipping_tracking_id', 'shipping_price', 'order_subtotal', 'order_tax', 'order_total', 'order_total_dim_h', 'order_total_dim_l', 'order_total_dim_w', 'order_total_weight', 'contains_exchange_unit', 'exchange_unit_img', 'is_cancelled', 'is_completed', 'current_status_id', 'current_status_date', 'current_status_comment']

class OrderItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.OrderItems
        fields = ['order_item_id', 'order_id', 'sku_no', 'order_item_price']

class OrderHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.OrderHistory
        fields = ['order_history_id', 'order_id', 'status_id', 'status_date', 'status_comment']

class OrderCommunicationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.OrderCommunicationHistory
        fields = ['comm_id', 'user_id', 'order_id', 'comm_method', 'comm_type', 'comm_recipient', 'comm_date', 'comm_subject', 'comm_comment']

# Invoice Model Serializers

class InvoicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.Invoices
        fields = ['invoice_id', 'user_id', 'order_id', 'download_link', 'is_synced', 'sage_id', 'sage_doc_no']

class InvoiceItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.InvoiceItems
        fields = ['invoice_item_id', 'invoice_id', 'order_item_id']

# Repair Model Serializer

class RepairsSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.Repairs
        fields = ['repair_id', 'user_id', 'repair_date', 'product_id', 'reason_repair', 'shipping_address_id', 'shipping_method_id', 'shipping_tracking_id', 'shipping_price_excl', 'shipping_price_incl', 'shipping_price_tax', 'is_cancelled', 'is_completed', 'current_status_id', 'current_status_date', 'current_status_comment']

class RepairHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.RepairHistory
        fields = ['repair_history_id', 'repair_id', 'status_id', 'status_date', 'status_comment']

class RepairCommunicationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.RepairCommunicationHistory
        fields = ['comm_id', 'user_id', 'repair_id', 'comm_method', 'comm_type', 'comm_recipient', 'comm_date', 'comm_subject', 'comm_comment']

# Return Model Serializers

class ReturnsSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.Returns
        fields = ['return_id', 'user_id', 'order_id', 'order_item_id', 'reason_return', 'product_problem', 'is_completed', 'preferred_outcome', 'current_status_id', 'current_status_date', 'current_status_comment']

class ReturnHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = auth_models.ReturnHistory
        fields = ['return_history_id', 'return_id', 'status_id', 'status_date', 'status_comment']

class ReturnCommunicationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.ReturnCommunicationHistory
        fields = ['comm_id', 'user_id', 'return_id', 'comm_method', 'comm_type', 'comm_recipient', 'comm_date', 'comm_subject', 'comm_comment']
