from rest_framework import viewsets, status, views
from . import admin_permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch
from .admin_mixins import UniversalAdminMixin

class ProductAdminViewSet(UniversalAdminMixin, viewsets.ViewSet):

    def list(self, request):
        '''
        list products, models, stock
        '''
        items = {
            'products': {},
            'stocks': {},
            'models': {}
        }
        data = self.fetch_list(items=items)
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        '''
        get product details, including related:
        - models
        - stock
        '''
        self.item_type = 'products'
        related = {
            'models': {},
            'stocks': {
                'select_related': ['product_config_id']
            },
            'orders': {
                'item_hierachy': 'child',
                'select_related': ['sku_no__product_config_id']
            },
            'repairs': {},
            'invoices': {
                'item_hierachy': 'child',
                'select_related': ['order_item_id__sku_no__product_config_id']
            },
            'returns': {
                'select_related': ['order_item_id__sku_no__product_config_id']
            }
        }
        data = self.fetch_main(pk=pk, related=related)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True)
    def stock(self, request, pk=None):
        '''
        get stock details, including related:
        - orders
        - invoices
        - returns
        '''
        self.item_type = 'stocks'
        related = {
            'orders': {
                'item_hierachy': 'child'
            },
            'invoices': {
                'item_hierachy': 'child',
                'select_related': ['order_item_id__sku_no']
            },
            'returns': {}
        }
        data = self.fetch_main(pk=pk, related=related)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True)
    def models(self, request, pk=None):
        '''
        get model details
        '''
        self.item_type = 'model'
        data = self.fetch_main(pk=pk)
        return Response(data, status=status.HTTP_200_OK)

class CategoriesAdminViewSet(UniversalAdminMixin, viewsets.ViewSet):

    def list(self, request):
        '''
        list categories and brands
        '''
        items = {
            'categories': {},
            'brands': {}
        }
        data = self.fetch_list(items=items)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True)
    def category(self, request, pk=None):
        '''
        get category details, including related:
        - products
        '''
        self.item_type = 'categories'
        related = {
            'products': {}
        }
        data = self.fetch_main(pk=pk, related=related)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True)
    def brand(self, request, pk=None):
        '''
        get brand details, including related:
        - products
        '''
        self.item_type = 'brands'
        related = {
            'products': {}
        }
        data = self.fetch_main(pk=pk, related=related)
        return Response(data, status=status.HTTP_200_OK)

class OrdersAdminViewSet(UniversalAdminMixin, viewsets.ViewSet):
    
    def list(self, request):
        '''
        list orders
        '''
        items = {
            'orders': {}
        }
        data = self.fetch_list(items=items)
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        '''
        get order details, including related:
        - exchange unit photos
        - invoices
        - returns
        - communication
        - history
        '''
        self.item_type = 'orders'
        related = {
            'invoices': {},
            'returns': {}
        }
        data = self.fetch_main(pk=pk, related=related, comm_history=True)
        return Response(data, status=status.HTTP_200_OK)

class InvoicesAdminViewSet(UniversalAdminMixin, viewsets.ViewSet):

    def list(self, request):
        '''
        list invoices
        '''
        items = {
            'invoices': {
                'prefetch_related': ['order_id']
            }
        }
        data = self.fetch_list(items=items)
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        '''
        get invoice details, including related:
        - orders
        - returns
        '''
        self.item_type = 'invoices'
        related = {
            'orders': {},
            'returns': {
                'item_hierachy': 'reverse',
                'parent_id_field': 'order_id'
            }
        }
        data = self.fetch_main(pk=pk, related=related)
        return Response(data, status=status.HTTP_200_OK)

class RepairsAdminViewSet(UniversalAdminMixin, viewsets.ViewSet):

    def list(self, request):
        '''
        list repairs
        '''
        items = {
            'repairs': {
                'prefetch_related': ['product_id']
            }
        }
        data = self.fetch_list(items=items)
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        '''
        list repair details, including related:
        - communication
        - history
        '''
        self.item_type = 'repairs'
        data = self.fetch_main(pk=pk, comm_history=True)
        return Response(data, status=status.HTTP_200_OK)

class ReturnsAdminViewSet(UniversalAdminMixin, viewsets.ViewSet):
    
    def list(self, request):
        '''
        list returns
        '''
        items = {
            'returns': {
                'prefetch_related': ['order_item_id__sku_no']
            }
        }
        data = self.fetch_list(items=items)
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        '''
        get return details, including related:
        - orders
        - invoices
        - communication
        - history
        '''
        self.item_type = 'returns'
        related = {
            'orders': {
                'item_hierachy': 'reverse'
            },
            'invoices': {
                'item_hierachy': 'reverse',
                'parent_id_field': 'order_id'
            }
        }
        data = self.fetch_main(pk=pk, related=related, comm_history=True)
        return Response(data, status=status.HTTP_200_OK)

class CustomersAdminViewSet(UniversalAdminMixin, viewsets.ViewSet):

    def list(self, request):
        '''
        list customers
        '''
        items = {
            'details': {}
        }
        data = self.fetch_list(items=items)
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        '''
        get customer details, including related:
        addresses
        orders
        invoices
        returns
        communication
        '''
        self.item_type = 'details'
        related = {
            'addresses': {},
            'orders': {},
            'invoices': {},
            'repairs': {},
            'returns': {},
            'orders_comm_history': {},
            'invoices_comm_history': {},
            'repairs_comm_history': {},
            'returns_comm_history': {}
        }
        data = self.fetch_main(pk=pk, related=related)
        return Response(data, status=status.HTTP_200_OK)

class SettingsAdminViewSet(UniversalAdminMixin, viewsets.ViewSet):

    def list(self, request):
        '''
        list statuses
        '''
        items = {
            'statuses': {}
        }
        data = self.fetch_list(items=items)
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        '''
        get status details
        '''
        self.item_type = 'statuses'
        data = self.fetch_main(pk=pk)
        return Response(data, status=status.HTTP_200_OK)