from rest_framework import viewsets, status, views
from . import admin_permissions
from .. import mixins as custom_mixins, serializers as custom_serializers, utils as custom_utils
from ..standard import st_serializers, st_models
from ..reg import reg_serializers, reg_models
from ..auth import auth_model_serializers
from . import admin_model_serializers

class ProductsAdminViewSet(viewsets.ModelViewSet):
    queryset = st_models.Products.objects.all()
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    serializer_class = st_serializers.ProductsSerializer()

class ProductConfigAdminViewSet(viewsets.ModelViewSet):
    # queryset = st_models.ProductConfig.objects.all()
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    serializer_class = st_serializers.ProductConfigSerializer()

    def get_queryset(self):
        

class ProductModelsAdminViewSet(viewsets.ModelViewSet):
    queryset = st_models.ProductModels.objects.all()
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    serializer_class = st_serializers.ProductModelsSerializer()

class ProductStockAdminViewSet(viewsets.ModelViewSet):
    queryset = st_models.ProductStock.objects.all()
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    serializer_class = st_serializers.ProductStockSerializer()

class BrandsAdminViewSet(viewsets.ModelViewSet):
    queryset = st_models.Brands.objects.all()
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    serializer_class = st_serializers.BrandsSerializer()

class CategoriesAdminViewSet(viewsets.ModelViewSet):
    queryset = st_models.Categories.objects.all()
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    serializer_class = st_serializers.CategoriesSerializer()

class StatusesAdminViewSet(viewsets.ModelViewSet):
    queryset = st_models.Statuses.objects.all()
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    serializer_class = st_serializers.StatusesSerializer()

class UserLoginAdminViewSet(viewsets.ModelViewSet):
    queryset = reg_models.UserLogin.objects.all()
    permission_classes = [admin_permissions.AdminObjectType2Permission]
    serializer_class = admin_model_serializers.UserLoginAdminSerializer()

class UserDetailsAdminViewSet(viewsets.ModelViewSet):
    queryset = reg_models.UserDetails.objects.all()
    permission_classes = [admin_permissions.AdminObjectType4Permission]
    serializer_class = admin_model_serializers.UserDetailsAdminSerializer()

class UserAddressesAdminViewSet(viewsets.ModelViewSet):
    queryset = reg_models.UserAddresses.objects.all()
    permission_classes = [admin_permissions.AdminObjectType1Permission]
    serializer_class = auth_model_serializers.UserAddressSerializer()

class OrdersAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.Orders.objects.all()
    permission_classes = [admin_permissions.AdminObjectType3Permission]
    serializer_class = admin_model_serializers.OrdersAdminSerializer()

class OrderItemsAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.OrderItems.objects.all()
    permission_classes = [admin_permissions.AdminObjectType5Permission]
    serializer_class = auth_model_serializers.OrderItemsSerializer()

class OrderHistoryAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.OrderHistory.objects.all()
    permission_classes = [admin_permissions.AdminObjectType5Permission]
    serializer_class = auth_model_serializers.OrderHistorySerializer()

class OrderCommunicationHistoryAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.OrderCommunicationHistory.objects.all()
    permission_classes = [admin_permissions.AdminObjectType4Permission]
    serializer_class = auth_model_serializers.OrderCommunicationHistorySerializer()

class InvoiceAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.Invoices.objects.all()
    permission_classes = [admin_permissions.AdminObjectType4Permission]
    serializer_class = auth_model_serializers.InvoicesSerializer()

class InvoiceItemsAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.InvoiceItems.objects.all()
    permission_classes = [admin_permissions.AdminObjectType4Permission]
    serializer_class = auth_model_serializers.InvoiceItemsSerializer()

class ReturnsAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.Returns.objects.all()
    permission_classes = [admin_permissions.AdminObjectType3Permission]
    serializer_class = admin_model_serializers.ReturnsAdminSerializer()

class ReturnHistoryAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.ReturnHistory.objects.all()
    permission_classes = [admin_permissions.AdminObjectType5Permission]
    serializer_class = auth_model_serializers.ReturnHistorySerializer()

class ReturnCommunicationHistoryAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.ReturnCommunicationHistory.objects.all()
    permission_classes = [admin_permissions.AdminObjectType4Permission]
    serializer_class = auth_model_serializers.ReturnCommunicationHistorySerializer()

class RepairsAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.Repairs.objects.all()
    permission_classes = [admin_permissions.AdminObjectType3Permission]
    serializer_class = admin_model_serializers.RepairsAdminSerializer()

class RepairHistoryAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.RepairHistory.objects.all()
    permission_classes = [admin_permissions.AdminObjectType5Permission]
    serializer_class = auth_model_serializers.RepairHistorySerializer()

class RepairCommunicationHistoryAdminViewSet(viewsets.ModelViewSet):
    queryset = auth_models.RepairCommunicationHistory.objects.all()
    permission_classes = [admin_permissions.AdminObjectType4Permission]
    serializer_class = auth_model_serializers.RepairCommunicationHistorySerializer()