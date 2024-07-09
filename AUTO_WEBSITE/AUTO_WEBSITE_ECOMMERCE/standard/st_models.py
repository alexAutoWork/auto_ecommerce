from django.db import models
from rest_framework import filters

#Status Model

class Statuses(models.Model):
    status_id = models.AutoField(primary_key=True, db_column='status_id')
    status_type = models.CharField(max_length=45)
    status_value = models.CharField(max_length=45)
    is_active = models.BooleanField()
    #synced

    class Meta:
        managed = False
        db_table = 'statuses'

# Product Models

class BrandSeq(models.Model):
    brand_seq_id = models.AutoField(primary_key=True, db_column='id')
    #synced
    
    class Meta:
        managed = False
        db_table = 'brand_seq'


class Brands(models.Model):
    brand_id = models.CharField(primary_key=True, max_length=45, db_column='brand_id')
    brand_value = models.CharField(max_length=45)
    #synced

    class Meta:
        managed = False
        db_table = 'brands'


class Categories(models.Model):
    category_id = models.CharField(primary_key=True, max_length=45, db_column='category_id')
    category_value = models.CharField(max_length=45)
    #synced

    class Meta:
        managed = False
        db_table = 'categories'


class CategorySeq(models.Model):
    category_seq_id = models.AutoField(primary_key=True, db_column='id')
    #synced

    class Meta:
        managed = False
        db_table = 'category_seq'

class Variations(models.Model):
    variation_id = models.AutoField(primary_key=True, db_column='variation_id')
    variation_value = models.CharField(max_length=45)
    #synced

    class Meta:
        managed = False
        db_table = 'variations'

class Products(models.Model):
    product_id = models.CharField(primary_key=True, max_length=45, db_column='product_id')
    name = models.CharField(max_length=45)
    weight = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    weight_type = models.CharField(max_length=45)
    dimension_h = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    dimension_l = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    dimension_w = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    brand_id = models.ForeignKey(Brands, on_delete=models.RESTRICT, db_column='brand_id')
    category_id = models.ForeignKey(Categories, on_delete=models.RESTRICT, db_column='category_id')
    product_img = models.CharField(max_length=500)
    product_img_thumb = models.CharField(max_length=500)
    warranty = models.CharField(max_length=20)
    is_repairable = models.BooleanField()
    stock_available = models.IntegerField()
    is_active = models.BooleanField()
    has_stock = models.BooleanField()
    #synced

    def check_stock_available(self, products_id):
        self.products_id = products_id
        queryset = ProductStock.objects.filter(is_purchased=False).prefetch_related('product_config_id').filter(products_id=products_id)
        return queryset.count()

    def update_stock_available(self):
        self.stock_available = check_stock_available()
        self.save(update_fields=['stock_available'])

    class Meta:
        managed = False
        db_table = 'products'

class ProductConfig(models.Model):
    product_config_id = models.AutoField(primary_key=True, db_column='product_config_id')
    product_id = models.ForeignKey(Products, on_delete=models.RESTRICT, db_column='product_id')
    variation_id = models.ForeignKey(Variations, on_delete=models.RESTRICT, db_column='variation_id')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_synced = models.BooleanField()
    sage_id = models.IntegerField(unique=True, blank=True, null=True)
    sage_item_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    stock_available = models.IntegerField()
    has_stock = models.BooleanField()
    #synced

    class Meta:
        managed = False
        db_table = 'product_config'


class ProductModels(models.Model):
    model_number = models.CharField(primary_key=True, max_length=45, db_column='model_number')
    product_id = models.ForeignKey(Products, on_delete=models.RESTRICT, db_column='product_id')
    #synced

    class Meta:
        managed = False
        db_table = 'product_models'


class ProductStocks(models.Model):
    sku_no = models.CharField(primary_key=True, max_length=45, db_column='sku_no')
    product_config_id = models.ForeignKey(ProductConfig, on_delete=models.RESTRICT, db_column='product_config_id')
    is_purchased = models.BooleanField()
    current_status_id = models.ForeignKey(Statuses, on_delete=models.RESTRICT, db_column='current_status_id')
    current_status_date = models.DateTimeField()
    current_status_comment = models.TextField(blank=True, null=True)
    #synced

    class Meta:
        managed = False
        db_table = 'product_stock'

# Shipping Models

class ShippingMethods(models.Model):
    shipping_method_id = models.AutoField(primary_key=True, db_column='shipping_method_id')
    shipping_method_value = models.CharField(max_length=45)
    #synced

    class Meta:
        managed = False
        db_table = 'shipping_methods'

class Cities(models.Model):
    city_id = models.AutoField(primary_key=True, db_column='city_id')
    city_value = models.CharField(max_length=45)
    ram_address_1 = models.CharField(max_length=45)
    local_area = models.CharField(max_length=45)
    region_code = models.CharField(max_length=45)
    postal_code = models.CharField(max_length=45)
    #synced

    class Meta:
        managed = False
        db_table = 'cities'

class BaseShippingRates(models.Model):
    base_shipping_rate_id = models.AutoField(primary_key=True, db_column='base_shipping_rate_id')
    city_id = models.ForeignKey(Cities, on_delete=models.CASCADE, db_column='city_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    base_charge = models.DecimalField(max_digits=12, decimal_places=2)
    #synced

    class Meta:
        managed = False
        db_table = 'base_shipping_rates'