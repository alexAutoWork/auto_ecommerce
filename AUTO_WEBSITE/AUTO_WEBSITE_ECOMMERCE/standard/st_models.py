from django.db import models
from rest_framework import filters

# Product Models

class BrandSeq(models.Model):
    brand_seq_id = models.AutoField(primary_key=True, db_column='id')
    
    class Meta:
        managed = False
        db_table = 'brand_seq'


class Brands(models.Model):
    brands_id = models.CharField(primary_key=True, max_length=45)
    value = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'brands'


class Categories(models.Model):
    categories_id = models.CharField(primary_key=True, max_length=45)
    value = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'categories'


class CategorySeq(models.Model):
    category_seq_id = models.AutoField(primary_key=True, db_column='id')

    class Meta:
        managed = False
        db_table = 'category_seq'

class Variations(models.Model):
    variation_id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'variations'

class Products(models.Model):
    products_id = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=45)
    weight = models.DecimalField(max_digits=12, decimal_places=4)
    dimension_h = models.DecimalField(max_digits=12, decimal_places=4)
    dimension_l = models.DecimalField(max_digits=12, decimal_places=4)
    dimension_w = models.DecimalField(max_digits=12, decimal_places=4)
    brands_id = models.ForeignKey(Brands, on_delete=models.RESTRICT)
    categories_id = models.ForeignKey(Categories, on_delete=models.RESTRICT)
    product_img = models.CharField(max_length=500)
    product_img_thumb = models.CharField(max_length=500)
    warranty = models.CharField(max_length=20)
    is_repairable = models.BooleanField()
    stock_available = models.IntegerField()
    is_active = models.BooleanField()

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
    product_config_id = models.AutoField(primary_key=True)
    products_id = models.ForeignKey(Products, on_delete=models.RESTRICT)
    variation_id = models.ForeignKey(Variations, on_delete=models.RESTRICT)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_synced = models.BooleanField()
    sage_id = models.IntegerField(unique=True, blank=True, null=True)
    sage_item_id = models.CharField(max_length=100, unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_config'


class ProductModels(models.Model):
    model_number = models.CharField(primary_key=True, max_length=45)
    products_id = models.ForeignKey(Products, on_delete=models.RESTRICT)

    class Meta:
        managed = False
        db_table = 'product_models'


class ProductStock(models.Model):
    sku_no = models.CharField(primary_key=True, max_length=45)
    product_config_id = models.ForeignKey(ProductConfig, on_delete=models.RESTRICT)
    is_purchased = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'product_stock'

# Shipping Models

class ShippingMethod(models.Model):
    shipping_method_id = models.AutoField(primary_key=True, db_column='id')
    value = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'shipping_method'

class Cities(models.Model):
    city_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=45)
    ram_address_1 = models.CharField(max_length=45)
    ram_address_2 = models.CharField(max_length=45)
    region = models.CharField(max_length=45)
    postal_code = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'cities'

class BaseShippingRates(models.Model):
    shipping_rate_id = models.AutoField(primary_key=True)
    city_id = models.ForeignKey(Cities, on_delete=models.CASCADE)
    products_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    base_charge = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'base_shipping_rates'

#Status Model

class Statuses(models.Model):
    id_status = models.AutoField(primary_key=True)
    status_type = models.CharField(max_length=45, db_column='type')
    value = models.CharField(max_length=45)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'statuses'