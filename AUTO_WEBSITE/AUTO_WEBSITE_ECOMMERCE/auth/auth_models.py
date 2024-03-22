# Model File Only Accessible with Authorization

from django.db import models
from ..reg.reg_models import UserLogin, UserAddresses
from ..standard import st_models

# Shopping Cart Models

class ShoppingCart(models.Model):
    shopping_cart_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    vat = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'shopping_cart'


class ShoppingCartItems(models.Model):
    shopping_cart_items_id = models.AutoField(primary_key=True)
    shopping_cart_id = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product_config_id = models.ForeignKey(st_models.ProductConfig, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'shopping_cart_items'

# Order Models

class Orders(models.Model):
    order_id = models.CharField(primary_key=True, max_length=45)
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT)
    order_date = models.DateTimeField()
    shipping_address_id = models.ForeignKey(UserAddresses, on_delete=models.SET_NULL, blank=True, null=True)
    shipping_method_id = models.ForeignKey(st_models.ShippingMethod, on_delete=models.RESTRICT)
    shipping_tracking_id = models.CharField(max_length=45)
    shipping_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    order_subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    order_tax = models.DecimalField(max_digits=12, decimal_places=2)
    order_total = models.DecimalField(max_digits=12, decimal_places=2)
    order_total_dim_h = models.DecimalField(max_digits=12, decimal_places=4)
    order_total_dim_l = models.DecimalField(max_digits=12, decimal_places=4)
    order_total_dim_w = models.DecimalField(max_digits=12, decimal_places=4)
    order_total_weight = models.DecimalField(max_digits=12, decimal_places=4)
    contains_exchange_unit = models.BooleanField()
    exchange_unit_img = models.JSONField(blank=True, null=True)
    is_cancelled = models.BooleanField()
    is_completed = models.BooleanField()
    current_status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT)
    current_status_date = models.DateTimeField()
    current_status_comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'

class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    sku_no = models.ForeignKey(st_models.ProductStock, on_delete=models.RESTRICT)
    order_item_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'order_items'

class OrderSeq(models.Model):
    order_seq_id = models.AutoField(primary_key=True, db_column='id')

    class Meta:
        managed = False
        db_table = 'order_seq'

class OrderHistory(models.Model):
    order_history_id = models.AutoField(primary_key=True, db_column='id')
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT)
    status_date = models.DateTimeField()
    status_comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_history'

class OrderCommunicationHistory(models.Model):
    comm_id = models.AutoField(primary_key=True, db_column='id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    comm_method = models.CharField(max_length=45)
    comm_type = models.CharField(max_length=45)
    comm_recipient = models.CharField(max_length=45)
    comm_date = models.DateTimeField()
    comm_subject = models.TextField()
    comm_comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'order_communication_history'

# Invoice Models

class Invoices(models.Model):
    invoice_id = models.CharField(primary_key=True, max_length=45)
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT)
    order_id = models.ForeignKey(Orders, on_delete=models.RESTRICT)
    download_link = models.CharField(max_length=500, blank=True, null=True)
    is_synced = models.BooleanField()
    sage_id = models.IntegerField(blank=True, null=True, unique=True)
    sage_doc_no = models.CharField(max_length=100, blank=True, null=True, unique=True)

    class Meta:
        managed = False
        db_table = 'invoices'

class InvoiceItems(models.Model):
    invoice_item_id = models.AutoField(primary_key=True)
    invoice_id = models.ForeignKey(Invoices, on_delete=models.CASCADE)
    order_item_id = models.ForeignKey(OrderItems, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'invoice_items'

class InvoiceSeq(models.Model):
    invoice_seq_id = models.AutoField(primary_key=True, db_column='id')

    class Meta:
        managed = False
        db_table = 'invoice_seq'

# Repair Models

class Repairs(models.Model):
    repair_id = models.CharField(primary_key=True, max_length=45)
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT)
    repair_date = models.DateTimeField()
    product_id = models.ForeignKey(st_models.Products, on_delete=models.RESTRICT)
    reason_repair = models.TextField()
    shipping_address_id = models.IntegerField(blank=True, null=True)
    shipping_method_id = models.IntegerField()
    shipping_tracking_id = models.CharField(max_length=45, blank=True, null=True)
    shipping_price_excl = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    shipping_price_incl = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    shipping_price_tax = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    is_cancelled = models.BooleanField()
    is_completed = models.BooleanField()
    current_status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT)
    current_status_date = models.DateTimeField()
    current_status_comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'repairs'

class RepairSeq(models.Model):
    repair_seq_id = models.AutoField(primary_key=True, db_column='id')

    class Meta:
        managed = False
        db_table = 'repair_seq'

class RepairHistory(models.Model):
    repair_history_id = models.AutoField(primary_key=True, db_column='id')
    repair_id = models.ForeignKey(Repairs, on_delete=models.CASCADE)
    status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT)
    status_date = models.DateTimeField()
    status_comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'repair_history'

class RepairCommunicationHistory(models.Model):
    comm_id = models.AutoField(primary_key=True, db_column='id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT)
    repair_id = models.ForeignKey(Repairs, on_delete=models.CASCADE)
    comm_method = models.CharField(max_length=45)
    comm_type = models.CharField(max_length=45)
    comm_recipient = models.CharField(max_length=45)
    comm_date = models.DateTimeField()
    comm_subject = models.TextField()
    comm_comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'repair_communication_history'

# Return Models

class Returns(models.Model):
    return_id = models.CharField(primary_key=True, max_length=45)
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT)
    order_id = models.ForeignKey(Orders, on_delete=models.RESTRICT)
    order_item_id = models.ForeignKey(OrderItems, on_delete=models.RESTRICT)
    reason_return = models.TextField()
    product_problem = models.TextField()
    is_completed = models.BooleanField()
    preferred_outcome = models.TextField()
    current_status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT)
    current_status_date = models.DateTimeField()
    current_status_comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'returns'


class ReturnsSeq(models.Model):
    return_seq_id = models.AutoField(primary_key=True, db_column='id')

    class Meta:
        managed = False
        db_table = 'returns_seq'

class ReturnHistory(models.Model):
    return_history_id = models.AutoField(primary_key=True, db_column='id')
    return_id = models.ForeignKey(Returns, on_delete=models.CASCADE)
    status_id = models.ForeignKey(st_models.Statuses, on_delete=models.RESTRICT)
    status_date = models.DateTimeField()
    status_comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'return_history'

class ReturnCommunicationHistory(models.Model):
    comm_id = models.AutoField(primary_key=True, db_column='id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT)
    return_id = models.ForeignKey(Returns, on_delete=models.CASCADE)
    comm_method = models.CharField(max_length=45)
    comm_type = models.CharField(max_length=45)
    comm_recipient = models.CharField(max_length=45)
    comm_date = models.DateTimeField()
    comm_subject = models.TextField()
    comm_comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'return_communication_history'