from rest_framework import serializers
from ..auth.auth_models import Orders, Repairs, Returns
from ..auth.auth_model_serializers import OrderItemsSerializer
from ..reg.reg_models import UserLogin, UserDetails
from ..reg.reg_serializers import UserAddressSerializer
from ..st.st_serializers import ProductsSerializer
from phonenumber_field import serializerfields

class OrdersAdminSerializer(serializers.ModelSerializer):
    shipping_address_id = UserAddressSerializer()
    current_status_id = serializers.SlugRelatedField(slug_field='value')
    shipping_method_id = serializers.SlugRelatedField(slug_field='value')

    class Meta:
        model = Orders
        fields = ['order_id', 'user_id', 'order_date', 'shipping_address_id', 'shipping_method_id', 'shipping_tracking_id', 'shipping_price', 'order_subtotal', 'order_tax', 'order_total', 'order_total_dim_h', 'order_total_dim_l', 'order_total_dim_w', 'order_total_weight', 'contains_exchange_unit', 'exchange_unit_img', 'is_cancelled', 'is_completed', 'current_status_id', 'current_status_date', 'current_status_comment']
        read_only_fields = ['order_id', 'user_id', 'order_date', 'shipping_address_id', 'shipping_method_id', 'shipping_tracking_id', 'shipping_price', 'order_subtotal', 'order_tax', 'order_total', 'order_total_dim_h', 'order_total_dim_l', 'order_total_dim_w', 'order_total_weight', 'contains_exchange_unit']

class RepairsAdminSerializer(serializers.ModelSerializer):
    product_id = ProductsSerializer()
    current_status_id = serializers.SlugRelatedField(slug_field='value')

    class Meta:
        model = Repairs
        fields = ['repair_id', 'user_id', 'repair_date', 'product_id', 'reason_repair', 'shipping_address_id', 'shipping_method_id', 'shipping_tracking_id', 'shipping_price_excl', 'shipping_price_incl', 'shipping_price_tax', 'is_cancelled', 'is_completed', 'current_status_id', 'current_status_date', 'current_status_comment']
        read_only_fields = ['repair_id', 'user_id', 'repair_date', 'product_id', 'reason_repair', 'shipping_address_id', 'shipping_method_id', 'shipping_tracking_id', 'shipping_price_excl', 'shipping_price_incl', 'shipping_price_tax']

class ReturnsAdminSerializer(serializers.ModelSerializer):
    current_status_id = serializers.SlugRelatedField(slug_field='value')
    order_item_id = OrderItemsSerializer()

    class Meta:
        model = Returns
        fields = ['return_id', 'user_id', 'order_id', 'order_item_id', 'reason_return', 'product_problem', 'is_completed', 'preferred_outcome', 'current_status_id', 'current_status_date', 'current_status_comment']
        read_only_fields = ['return_id', 'user_id', 'order_id', 'order_item_id', 'reason_return', 'product_problem', 'preferred_outcome']

class UserLoginAdminSerializer(serializers.ModelSerializer):
    mobile_no = serializerfields.PhoneNumberField()
    class Meta:
        model = UserLogin
        fields = ['id', 'email', 'mobile_no', 'created_at', 'is_blacklisted']
        read_only_fields = ['id', 'email', 'mobile_no', 'created_at']

class UserDetailsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['user_id', 'name', 'surname', 'company', 'default_address', 'company_reg_no', 'vat_no', 'is_synced']
        read_only_fields = ['user_id', 'name', 'surname', 'company', 'company_reg_no', 'vat_no']

