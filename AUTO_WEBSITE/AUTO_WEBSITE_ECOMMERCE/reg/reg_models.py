from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
import datetime

# User Creation Models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class UserLogin(AbstractUser):
    username = None
    is_superuser = None
    first_name = None
    last_name = None
    last_login = None
    is_staff = None
    date_joined = None
    groups = None
    user_permissions = None
    user_id = models.AutoField(primary_key=True, db_column='user_id')
    email = models.EmailField(_('email address'), unique=True)
    password = models.CharField(max_length=500)
    mobile_no = PhoneNumberField(max_length=45)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    created_at = models.DateTimeField(default=datetime.datetime.now())
    is_blacklisted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # synced

    def __str__(self):
        return self.email

    class Meta:
        managed = False
        db_table = 'user_login'

class UserAddresses(models.Model):
    address_id = models.AutoField(primary_key=True, db_column='address_id')
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, db_column='user_id')
    company = models.CharField(max_length=45, blank=True, null=True)
    name = models.CharField(max_length=45)
    unit_number = models.CharField(max_length=45, blank=True, null=True)
    address_line_1 = models.CharField(max_length=45)
    area = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    province = models.CharField(max_length=45)
    postal_code = models.CharField(max_length=45)
    contact_number = PhoneNumberField(max_length=45)
    email_address = models.EmailField(blank=True, null=True)
    # is_regional = models.BooleanField()
    is_active = models.BooleanField()
    is_default = models.BooleanField()
    #synced

    class Meta:
        managed = False
        db_table = 'user_addresses'

class UserDetails(models.Model):
    user_id = models.ForeignKey(UserLogin, on_delete=models.RESTRICT, primary_key=True, db_column='user_id')
    name = models.CharField(max_length=45)
    surname = models.CharField(max_length=45, blank=True, null=True)
    company = models.CharField(max_length=45, blank=True, null=True)
    default_address_id = models.ForeignKey(UserAddresses, on_delete=models.RESTRICT, blank=True, null=True, db_column='default_address_id')
    # shop_city = models.ForeignKey(Cities, on_delete=models.RESTRICT, blank=True, null=True)
    company_reg_no = models.CharField(max_length=45, blank=True, null=True)
    vat_no = models.IntegerField(blank=True, null=True)
    is_synced = models.BooleanField(default=False)
    sage_id = models.IntegerField(blank=True, null=True, unique=True)
    #synced, deleted shop_city_id

    class Meta:
        managed = False
        db_table = 'user_details'