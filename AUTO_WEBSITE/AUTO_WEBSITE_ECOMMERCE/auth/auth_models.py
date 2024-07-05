# Model File Only Accessible with Authorization

from django.db import models
from ..reg.reg_models import UserLogin, UserAddresses
from ..standard import st_models

# Shopping Cart Models

class ShoppingCart(models.Model):
    shopping_cart_id = models.AutoField(primary_key=True, db_column='shopping_cart_id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    vat = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    #synced

    class Meta:
        managed = False
        db_table = 'shopping_cart'


class ShoppingCartItems(models.Model):
    shopping_cart_item_id = models.AutoField(primary_key=True, db_column='shopping_cart_item_id')
    shopping_cart_id = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, db_column='shopping_cart_id')
    product_config_id = models.ForeignKey(st_models.ProductConfig, on_delete=models.CASCADE, db_column='product_config_id')
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    #synced

    class Meta:
        managed = False
        db_table = 'shopping_cart_items'

# Order Models

class Orders(models.Model):
    order_id = models.CharField(primary_key=True, max_length=45, db_column='order_id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    order_date = models.DateTimeField()
    shipping_address_id = models.ForeignKey(UserAddresses, on_delete=models.SET_NULL, blank=True, null=True, db_column='shipping_address_id')
    shipping_method_id = models.ForeignKey(st_models.ShippingMethods, on_delete=models.RESTRICT, db_column='shipping_method_id')
    shipping_tracking_id = models.CharField(max_length=45)
    order_quantity = models.IntegerField()
    order_subtotal_excl = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    order_subtotal_incl = models.DecimalField(max_digits=12, decimal_places=2)
    order_tax = models.DecimalField(max_digits=12, decimal_places=2)
    order_total = models.DecimalField(max_digits=12, decimal_places=2)
    contains_exchange_unit = models.BooleanField()
    is_cancelled = models.BooleanField()
    is_completed = models.BooleanField()
    current_status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT, db_column='current_status_id')
    current_status_date = models.DateTimeField()
    current_status_comment = models.TextField(blank=True, null=True)
    #synced

    class Meta:
        managed = False
        db_table = 'orders'

class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True, db_column='order_item_id')
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE, db_column='order_id')
    sku_no = models.ForeignKey(st_models.ProductStocks, on_delete=models.RESTRICT, db_column='sku_no', unique=True)
    order_item_excl = models.DecimalField(max_digits=12, decimal_places=2)
    order_item_vat = models.DecimalField(max_digits=12, decimal_places=2)
    order_item_incl = models.DecimalField(max_digits=12, decimal_places=2)
    #synced

    class Meta:
        managed = False
        db_table = 'order_items'

class OrderSeq(models.Model):
    order_seq_id = models.AutoField(primary_key=True, db_column='id')
    #synced

    class Meta:
        managed = False
        db_table = 'order_seq'

class OrderExUnitImages(models.Model):
    order_ex_unit_filename = models.CharField(max_length=45)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE, db_column='order_id')

    class Meta:
        managed = False
        db_table = 'order_ex_unit_images'

class OrderHistory(models.Model):
    history_id = models.AutoField(primary_key=True, db_column='history_id')
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE, db_column='order_id')
    status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT, db_column='status_id')
    status_date = models.DateTimeField()
    status_comment = models.TextField(blank=True, null=True)
    #synced

    class Meta:
        managed = False
        db_table = 'order_history'

class OrderCommunicationHistory(models.Model):
    comm_id = models.AutoField(primary_key=True, db_column='comm_id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE, db_column='order_id')
    comm_method = models.CharField(max_length=45)
    comm_type = models.CharField(max_length=45)
    comm_recipient = models.CharField(max_length=45)
    comm_date = models.DateTimeField()
    comm_subject = models.TextField()
    comm_comment = models.TextField()
    #synced

    class Meta:
        managed = False
        db_table = 'order_communication_history'

# Invoice Models

class Invoices(models.Model):
    invoice_id = models.CharField(primary_key=True, max_length=45, db_column='invoice_id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    order_id = models.ForeignKey(Orders, on_delete=models.RESTRICT, db_column='order_id')
    download_link = models.CharField(max_length=500, blank=True, null=True)
    is_synced = models.BooleanField()
    sage_id = models.IntegerField(blank=True, null=True, unique=True)
    sage_doc_no = models.CharField(max_length=100, blank=True, null=True, unique=True)
    #synced

    class Meta:
        managed = False
        db_table = 'invoices'

class InvoiceItems(models.Model):
    invoice_item_id = models.AutoField(primary_key=True, db_column='invoice_item_id')
    invoice_id = models.ForeignKey(Invoices, on_delete=models.CASCADE, db_column='invoice_id')
    order_item_id = models.ForeignKey(OrderItems, on_delete=models.CASCADE, db_column='order_item_id')
    #synced

    class Meta:
        managed = False
        db_table = 'invoice_items'

class InvoiceSeq(models.Model):
    invoice_seq_id = models.AutoField(primary_key=True, db_column='id')
    #synced

    class Meta:
        managed = False
        db_table = 'invoice_seq'

# Repair Models

class Repairs(models.Model):
    repair_id = models.CharField(primary_key=True, max_length=45, db_column='repair_id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    repair_date = models.DateTimeField()
    product_id = models.ForeignKey(st_models.Products, on_delete=models.RESTRICT, db_column='product_id')
    reason_repair = models.TextField()
    error_codes = models.TextField()
    shipping_address_id = models.ForeignKey(UserAddresses, on_delete=models.SET_NULL, blank=True, null=True, db_column='shipping_address_id')
    shipping_method_id = models.ForeignKey(st_models.ShippingMethods, on_delete=models.RESTRICT, db_column='shipping_method_id')
    shipping_tracking_id = models.CharField(max_length=45, blank=True, null=True)
    shipping_price_excl = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    shipping_price_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    shipping_price_tax = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    is_cancelled = models.BooleanField()
    is_completed = models.BooleanField()
    current_status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT, db_column='current_status_id')
    current_status_date = models.DateTimeField()
    current_status_comment = models.TextField(blank=True, null=True)
    #synced

    class Meta:
        managed = False
        db_table = 'repairs'

class RepairSeq(models.Model):
    repair_seq_id = models.AutoField(primary_key=True, db_column='id')
    #synced

    class Meta:
        managed = False
        db_table = 'repair_seq'

class RepairHistory(models.Model):
    history_id = models.AutoField(primary_key=True, db_column='history_id')
    repair_id = models.ForeignKey(Repairs, on_delete=models.CASCADE, db_column='repair_id')
    status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT, db_column='status_id')
    status_date = models.DateTimeField()
    status_comment = models.TextField(blank=True, null=True)
    #synced

    class Meta:
        managed = False
        db_table = 'repair_history'

class RepairCommunicationHistory(models.Model):
    comm_id = models.AutoField(primary_key=True, db_column='comm_id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    repair_id = models.ForeignKey(Repairs, on_delete=models.CASCADE, db_column='repair_id')
    comm_method = models.CharField(max_length=45)
    comm_type = models.CharField(max_length=45)
    comm_recipient = models.CharField(max_length=45)
    comm_date = models.DateTimeField()
    comm_subject = models.TextField()
    comm_comment = models.TextField()
    #synced

    class Meta:
        managed = False
        db_table = 'repair_communication_history'

# Return Models

class Returns(models.Model):
    return_id = models.CharField(primary_key=True, max_length=45, db_column='return_id')
    return_date = models.DateTimeField()
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    order_id = models.ForeignKey(Orders, on_delete=models.RESTRICT, db_column='order_id')
    order_item_id = models.ForeignKey(OrderItems, on_delete=models.RESTRICT, db_column='order_item_id')
    reason_return = models.TextField()
    product_problem = models.TextField()
    is_completed = models.BooleanField()
    preferred_outcome = models.TextField()
    current_status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT, db_column='current_status_id')
    current_status_date = models.DateTimeField()
    current_status_comment = models.TextField(blank=True, null=True)
    #synced

    class Meta:
        managed = False
        db_table = 'returns'


class ReturnsSeq(models.Model):
    return_seq_id = models.AutoField(primary_key=True, db_column='id')
    #synced

    class Meta:
        managed = False
        db_table = 'returns_seq'

class ReturnHistory(models.Model):
    history_id = models.AutoField(primary_key=True, db_column='history_id')
    return_id = models.ForeignKey(Returns, on_delete=models.CASCADE, db_column='return_id')
    status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT, db_column='status_id')
    status_date = models.DateTimeField()
    status_comment = models.TextField(blank=True, null=True)
    #synced

    class Meta:
        managed = False
        db_table = 'return_history'

class ReturnCommunicationHistory(models.Model):
    comm_id = models.AutoField(primary_key=True, db_column='comm_id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    return_id = models.ForeignKey(Returns, on_delete=models.CASCADE, db_column='return_id')
    comm_method = models.CharField(max_length=45)
    comm_type = models.CharField(max_length=45)
    comm_recipient = models.CharField(max_length=45)
    comm_date = models.DateTimeField()
    comm_subject = models.TextField()
    comm_comment = models.TextField()
    #synced

    class Meta:
        managed = False
        db_table = 'return_communication_history'