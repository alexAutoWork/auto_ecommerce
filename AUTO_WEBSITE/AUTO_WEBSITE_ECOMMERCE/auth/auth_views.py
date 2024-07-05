from rest_framework import viewsets, status, views, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from . import auth_models, auth_model_serializers, auth_serializers, auth_utils, auth_permissions, auth_mixins
from .. import serializers as custom_serializers, utils as custom_utils, mixins as custom_mixins, exceptions as custom_exceptions
from django.http import Http404
from django.conf import settings
from ..reg.reg_model_serializers import UserAddressesSerializer
from ..reg import reg_models
from ..standard import st_models
from ..external_api import external_api_views
import re, random, datetime, logging, json
from decimal import Decimal as dec
from django.db.models import Prefetch, F
from django.core.cache import cache
from django.core.files.storage import default_storage

sage = external_api_views.SageAccountingIntegration
vat_perc = dec(0.15)
logger = logging.getLogger(__name__)

class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = [auth_permissions.BaseAuthUserPermission]

    parent_serializer = auth_model_serializers.ShoppingCartSerializer
    child_serializer = auth_model_serializers.ShoppingCartItemsSerializer
    child_serializer_ex = auth_serializers.ShoppingCartItemsSerializerEx

    parent_model = auth_models.ShoppingCart
    child_model = auth_models.ShoppingCartItems

    shopping_cart_obj = None
    shopping_cart_items_obj = None

    def create_shopping_cart(self, request):
        user = request.user
        shopping_cart_obj = parent_model.objects.create(user_id=user.user_id)
        self.shopping_cart_obj = shopping_cart_obj
        return True

    def serialized_response(self, **kwargs):
        data = {}
        backend_req = kwargs.get('backend_req', False)
        exclude = kwargs.get('exclude', None)
        if self.serializer_cart_obj is not None:
            serializer1 = self.parent_serializer(self.serializer_cart_obj)
            data.append(**{'shopping_cart': serializer1.data})
            if self.serializer_cart_items_obj is not None:
                serializer2 = self.child_serializer(self.serializer_cart_obj, many=True)
                data.append(**{'shopping_cart_items': serializer2.data})
            if exclude is not None:
                data.pop(exclude, '')
            if backend_req:
                return data
            else:
                return Response(data, status=status.HTTP_200_OK)

    def items_load(self):
        if self.shopping_cart_obj is not None:
            prefetch_query = Prefetch('product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id').filter(is_active=True))
            shopping_cart_items_obj = self.child_model.objects.prefetch_related(prefetch_query).filter(shopping_cart_id=shopping_cart_obj.pk)
            self.shopping_cart_items_obj = shopping_cart_items_obj

    def list(self, request, backend_req=False):
        user = request.user
        shopping_cart_obj = self.parent_model.objects.get(user_id=user.user_id)
        if shopping_cart_obj.exists():
            self.check_object_permissions(request, shopping_cart_obj)
            self.items_load()
            if not backend_req:
                return self.serialized_response()
        else:
            self.create_shopping_cart(request)
            if True:
                self.list(request)

    def check_quantity(self, **kwargs):
        obj = kwargs.get('obj', None)
        pk = kwargs.get('pk', None)
        quantity = kwargs.get('quantity', None)
        if obj is None:
            if pk is not None:
                obj = st_models.Products.objects.get(pk=pk)
        if quantity is not None:
            if quantity >= obj.stock_available - 2:
                return False
            else:
                return True

    def update(self, request):
        if self.shopping_cart_obj is not None:
            self.items_load()
            shopping_cart_items_cal = []
            for item in self.shopping_cart_items_obj:
                quantity = item.quantity
                total_price = item.total_price
                total_price *= quantity
                shopping_cart_items_cal.append([round(total_price, 2), quantity])
            subtotal = 0
            total_quantity = 0
            for item in shopping_cart_items_cal:
                subtotal += item[0]
                total_quantity += item[1]
            subtotal = dec(subtotal)
            vat = round((subtotal * vat_perc), 2)
            total = subtotal + vat
            self.shopping_cart_obj.update(subtotal=subtotal, vat=vat, total=total, total_quantity=total_quantity)
            self.shopping_cart_obj.refresh_from_db()

    def partial_update(self, pk=None, **kwargs):
        backend_req = kwargs.get('backend_req', False)
        if backend_req:
            quantity = kwargs.get('quantity', None)
            obj = kwargs.get('obj', None)
            if quantity is not None:
                obj.quantity += quantity
        else:
            quantity = request.data.get('quantity', None)
            if self.shopping_cart_items_obj is not None:
                for item in self.shopping_cart_items_obj:
                    if pk == item.pk:
                        obj = item
            if quantity is not None:
                obj.quantity = quantity
        check_quantity = self.check_quantity(obj=obj)
        if check_quantity == True:
            obj.save()
            self.update(request)
            return self.serialized_response()

    def create(self, request):
        if self.shopping_cart_obj is not None:
            data = request.data
            data['shopping_cart_id'] = self.shopping_cart_obj
            data['user_id'] = request.user.user_id
            serializer = self.parent_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.data
                if self.shopping_cart_items_obj is not None:
                    for item in self.shopping_cart_items_obj:
                        if item.product_config_id == data['product_config_id']:
                            return self.partial_update(request, obj=item.shopping_cart_item_id, backend_req=True, quantity=data['quantity'])
                        else:
                            serializer.save()
                            self.update(request)
                            return self.serialized_response()

    def destroy(self, request, pk=None):
        if self.shopping_cart_obj is not None:
            if self.shopping_cart_items_obj is not None:
                for item in self.shopping_cart_items_obj:
                    if item.pk == pk:
                        item.delete()
                        self.update(request)
                        return self.serialized_response()

class InvoicesViewSet(custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]

    parent_serializer = auth_model_serializers.InvoicesSerializer
    child_serializer = auth_model_serializers.InvoiceItemsSerializer

    parent_model = auth_models.Invoices
    parent_id_field = 'invoice_id'
    child_model = auth_models.InvoiceItems
    child_id_field = 'invoice_item_id'

    cache_list_fields = [parent_model, 'user_id']
    cache_retreive_fields = [parent_model, parent_id_field]

    # def_prefetch_queryset = Prefetch('order_item_id__sku_no__product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id'))

    def list(self, request):
        data = self.parent_model.objects.filter(user_id=request.user.user_id)
        serializer = self.parent_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, **kwargs):
        is_admin_req = kwargs.get('is_admin_req', False)
        invoice_serializer_dict = {}
        invoice_queryset = self.parent_model.objects.select_related().filter(pk=pk).first()
        if invoice_queryset is not None:
            self.check_object_permissions(request, invoice_queryset)
            invoice_serializer = self.parent_serializer(invoice_queryset)
            invoice_serializer_dict.update(**{'invoice_details': invoice_serializer.data})
        if is_admin_req:
            return [invoice_serializer_dict, invoice_queryset]
        else:
            return Response(invoice_serializer_dict, status=status.HTTP_200_OK)
    
    def render_pdf(self, request, **kwargs):
        invoice_instance = kwargs.get('invoice_instance', None)
        order_instance = kwargs.get('order_instance')
        order_items_instance = kwargs.get('order_items_instance')
        order_user_details = kwargs.get('order_user_details')
        if invoice_instance is not None:
            order_user = request.user
            invoice_initial = {'invoice': order_instance, 'customer': order_user_details}
            invoice_data = {}
            invoice_id = invoice_instance.pk
            invoice_data['invoice_id'] = invoice_id
            invoice_data['customer_email'] = order_user.email
            invoice_data['customer_mobile'] = order_user.mobile_no
            col_list = ['order_id', 'order_date', 'name', 'surname', 'company', 'company_reg_no', 'vat_no', 'order_subtotal_excl', 'shipping_price', 'order_subtotal_incl', 'order_tax', 'order_total']
            invoice_name = []
            for key, value in invoice_initial.items():
                for col in col_list:
                    attr = getattr(value, col, None)
                    if attr is not None:
                        if col == 'name' | 'surname':
                            invoice_name.append(col)
                        else:
                            if 'order' in col:
                                col_val = col.replace('order', key)
                            else:
                                col_val = f'{key}_{col}'
                            invoice_data.append({col_val: attr})
            invoice_data['invoice_name'] = ' '.join(invoice_name)
            invoice_items_data_list = []
            sku_no = 'sku_no'
            product_config_id = f'{sku_no}.product_config_id'
            col_list = [sku_no, f'{product_config_id}.product_id.name', f'{product_config_id}.product_id.pk', f'{product_config_id}.variation_id.variation_value', 'order_item_excl', 'order_item_vat', 'order_item_incl']
            for item in order_item_instance:
                invoice_item = {}
                for col in col_list:
                    attr = getattr(item, col)
                    if attr is not None:
                        col_val = col.replace('order_', '')
                        invoice_item.append(**{col_val: attr})
                invoice_items_data_list.append(invoice_item)
            invoice_data['invoice_items'] = invoice_items_data_list
            serializer = auth_serializers.InvoiceRenderSerializer(data=invoice_data)
            if serializer.is_valid(raise_exception=True):
                invoice_render_request = requests.post(url='http://host.docker.internal:8080/render-invoice', json=serializer.data)
                invoice_render_message = invoice_render_request.json()['message']
                if invoice_render_message == 'successful':
                    filedir = f'invoices/{invoice_id}/'
                    datetime = custom_utils.return_date_and_time()
                    keywords = {
                        'user': f'user_id_{order_user.user_id}',
                        'invoice': 'invoice'
                    }
                    filename = custom_utils.generate_filename(datetime=datetime, **keywords)
                    pdf_file = custom_utils.return_file(filedir=filedir, filename=filename)
                    if True:
                        file = os.path.join(settings.MEDIA_ROOT, filedir, filename)
                        invoice_instance.download_link = file
                        invoice_instance.save()
                        invoice.instance.refresh_from_db()
                        return file

    def create_invoice(self, request, **kwargs):
        order_instance = kwargs.get('order_instance', None)
        if order_instance is not None:
            order_items_instance = kwargs.get('order_items_instance')
            order_user_details = kwargs.get('order_user_details')
            data = {
                'user_id': request.user.user_id,
                'order_id': order_instance.pk,
                'is_synced': False
            }
            invoice_serializer = self.parent_serializer(data=data)
            if invoice_serializer.is_valid(raise_exception=True):
                invoice_instance = invoice_serializer.save()
                invoice_instance = self.parent_models.objects.get(pk=invoice_instance['invoice_id'])
                self.create_invoice_items(request)
                if True:
                    super().list_cache(user_id=request.user.user_id, delete=True)
                    return self.render_pdf(request, invoice_instance=invoice_instance, order_instance=order_instance, order_items_instance=order_items_instance, order_user_details=order_user_details)

    def create_invoice_items(self, request, **kwargs):
        invoice_instance = kwargs.get('invoice_instance', None)
        order_instance = kwargs.get('order_instance')
        order_items_instance = kwargs.get('order_items_instance')
        if invoice_instance is not None:
            invoice_item_list_data = []
            for item in order_item_instance:
                invoice_item_data = {
                    'invoice_id': invoice_instance,
                    'order_item_id': item.order_item_id
                }
                invoice_item_list_data.append(invoice_item_data)
            invoice_item_serializer = self.child_serializer(data=invoice_item_data, many=True)
            if invoice_item_serializer.is_valid(raise_exception=True):
                invoice_item_serializer.save()
                return True

class OrdersViewSet(InvoicesViewSet, custom_mixins.CommunicationViewSetMixin, custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]

    def_prefetch_queryset = Prefetch('sku_no__product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id'))

    parent_serializer = auth_model_serializers.OrdersSerializer
    # parent_serializer_ex = auth_serializers.OrdersSerializerEx
    child_serializer = auth_model_serializers.OrderItemsSerializer
    child_serializer_ex = auth_serializers.OrderItemsSerializerEx
    file_serializer = auth_model_serializers.OrderExUnitImagesSerializer

    parent_model = auth_models.Orders
    parent_id_field = 'order_id'
    child_model = auth_models.OrderItems
    child_id_field = 'order_item_id'
    file_model = auth_models.OrderExUnitImages
    file_id_field = 'order_ex_unit_filename'

    cache_field = 'user_id'

    history_serializer = auth_model_serializers.OrderHistorySerializer
    history_model = auth_models.OrderHistory

    comm_history_serializer = auth_model_serializers.OrderCommunicationHistorySerializer
    comm_history_model = auth_models.OrderCommunicationHistory

    is_admin_req = False

    custom_actions = ['render_conf']

    cache_list_fields = [parent_model, 'user_id']
    cache_retreive_fields = [parent_model, parent_id_field]
    cache_retreive_child_fields = [child_model, parent_id_field]

    pending_product_stock = None

    def list(self, request):
        queryset = super().list_cache(queryset=self.parent_model.objects, user_id=request.user.user_id, extra_fields=request.query_params)
        serializer = self.parent_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    # @action(detail=True)
    def render_conf(self, request):
        order_instance = kwargs.get('instance', None)
        if order_instance is not None:
            order_instance = self.parent_serializer(order_instance)
            cache = super().get_or_set(queryset=self.child_model.objects.prefetch_related(self.def_prefetch_queryset), order_id=order_instance.pk, return_cache_name=True)
            order_items_instance = cache[0]
            order_items_serializer = self.child_serializer(order_items_instance, many=True)
            invoice_download_link = super().create_invoice(request, order_instance=order_instance, order_items_instance=order_items_instance, order_user_details=kwargs.get('user_details'))
            data = {'order_details': order_instance.data, 'order_items': order_items_serializer.data, 'invoice_download_link': invoice_download_link}
            return data

    def retrieve(self, request, pk=None):
        order_serializer_dict = {}
        order_queryset = super().retrieve_cache(queryset=self.parent_model.objects, order_id=pk)
        if order_queryset is not None:
            self.check_object_permissions(request, order_queryset)
            order_serializer = self.parent_serializer(order_queryset)
            order_serializer_dict.update(**{'order_details': order_serializer.data})
            order_item_serializer = self.retrieve_items(request, pk=pk)
            order_serializer_dict.update(**{'order_items': order_item_serializer.data})
            order_history_queryset = self.history_model.objects.filter(order_id=pk)
            if order_history_queryset is not None:
                order_history_serializer = self.history_serializer(order_history_queryset, many=True)
                order_serializer_dict.update(**{'order_history': order_history_serializer.data})
        if is_admin_req:
            return order_serializer_dict
        else:
            return Response(order_serializer_dict, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def retrieve_items(self, request, pk=None):
        order_items_queryset = super().get_or_set(queryset=self.child_model.objects.prefetch_related(self.def_prefetch_queryset), order_id=pk)
        if order_items_queryset is not None:
            return self.child_serializer(order_items_queryset, many=True)

    def validate_exchange_unit_images(self, files, order_id):
        paths = []
        for filename in files:
            filename = request.session[filename]
            path = filename.get('path', None)
            is_active = filename.get('is_active', False)
            if path is not None:
                default_storage.exists(path)
                if True:
                    if is_active:
                        append = True
                    else:
                        default_storage.delete(path)
                        append = True
                else:
                    if is_active:
                        raise Exception
                    else:
                        append = True
                if append is True:
                    paths.append({'path': path, 'is_active': is_active})
        request.session[f'ex_images_{order_id}'] = paths
        return True

    def send_conf(self, request, **kwargs):
        kwargs['serializer_data'].pop('invoice_download_link', None)
        return super().send_conf(request, **kwargs)

    def update_status(self, request, **kwargs):
        return super().update_status(request, **kwargs)

    def create(self, request, **kwargs):
        initial = kwargs.get('initial', None)
        if initial is not None:
            checkout_total = initial.get('checkout_total')
            contains_ex = initial.get('checkout_contains_ex', False)
            data = {
                'user_id': request.user.user_id,
                'order_date': datetime.date.today(),
                'shipping_address_id': initial.get('shipping_address_id', None),
                'shipping_method_id': initial.get('shipping_method_id'),
                'order_subtotal_excl': checkout_total['subtotal_excl'],
                'shipping_price': checkout_total['shipping'],
                'order_quantity': checkout_total['total_quantity'],
                'order_subtotal_incl': checkout_total['subtotal_incl'],
                'order_tax': checkout_total['vat'],
                'order_total': checkout_total['total'],
                'contains_exchange_unit': contains_ex,
                'is_cancelled': False,
                'is_completed': False,
                'current_status_id': 1,
                'current_status_date': datetime.date.today()
            }
            if contains_ex is True:
                ex_unit_files = request.data.get('ex_unit_images', None)
                if ex_unit_files is not None:
                    ex_unit_files = self.validate_exchange_unit_images(ex_unit_files)
            serializer = self.parent_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                order_instance = serializer.save()
                order_instance = auth_models.Orders.objects.select_related('shipping_method_id', 'shipping_address_id').filter(pk=order_instance['order_id']).first()
                if order_instance is not None:
                    return order_instance
                else:
                    raise custom_exceptions.not_found_error('order')

    def update_or_delete_ex_images(self, request, **kwargs):
        order_instance = kwargs.get('order_instance', None)
        if order_instance is not None:
            order_id = order_instance.pk
            paths = request.session[f'ex_images_{order_id}']
            data = []
            for path in paths:
                path = path.get('path')
                is_active = path.get('is_active')
                if path is not None:
                    if is_active:
                        data.append(path)
                    else:
                        file = self.file_model.objects.get(pk=path)
                        if file is not None:
                            file.delete()
            serializer = self.file_serializer(data=data, many=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

    def update(self, request, **kwargs):
        order_instance = kwargs.get('order_instance')
        initial = kwargs.get('initial', None)
        if initial is not None:
            checkout_total = initial.get('checkout_total')
            contains_ex = initial.get('checkout_contains_ex', False)
            data = {
                'shipping_address_id': initial.get('shipping_address_id', None),
                'shipping_method_id': initial.get('shipping_method_id'),
                'order_subtotal_excl': checkout_total['subtotal_excl'],
                'shipping_price': checkout_total['shipping'],
                'order_quantity': checkout_total['total_quantity'],
                'order_subtotal_incl': checkout_total['subtotal_incl'],
                'order_tax': checkout_total['vat'],
                'order_total': checkout_total['total'],
            }
            if contains_ex is True:
                ex_unit_files = request.data.get('ex_unit_images', None)
                if ex_unit_files is not None:
                    ex_unit_files = self.validate_exchange_unit_images(ex_unit_files)
            order_instance.update(**data)
            order_instance.reload_from_db()
            return order_instance

    def return_random_stock(self, product_config_id):
        '''
        return random number from stock number list (defined in self.pending_product_stock) and pop from list
        used in create_order_items() for non duplicates of order items
        '''
        stock_number = super().filter_cache(data=self.pending_product_stock, fields={'product_config_id': product_config_id})
        self.pending_product_stock.pop(stock_number)
        return stock_number

    def create_order_items(self, request, **kwargs):
        items = kwargs.get('initial_data_items')
        order_instance = kwargs.get('order_instance')
        order_item_list_data = []
        product_configs = []
        for item in items:
            product_configs.append(item.product_config_id)
        self.pending_product_stock = ProductStocks.objects.filter(product_config_id__in=product_configs, is_purchased=False, is_pending=False)
        product_stock.update(is_pending=True)
        for item in items:
            product_config_id = item.product_config_id
            item_excl = item.total_price
            item_vat = round((item_excl * vat_perc), 2)
            order_item_data = {
                'product_config_id': product_config_id,
                'order_id': order_instance.order_id,
                'sku_no': self.return_random_stock(product_config_id),
                'order_item_excl': item_excl,
                'order_item_vat': item_vat,
                'order_item_incl': item_excl + item_vat
            }
            order_item_list_data.append(order_item_data)
        serializer = self.child_serializer(data=order_item_list_data, many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            super().list_cache(user_id=request.user.user_id, delete=True)
            return True

    def update_order_items(self, request, **kwargs):
        fields = kwargs.get('fields', None)
        order_instance = kwargs.get('order_instance')
        cache = super().get_or_set(queryset=self.child_model.objects.prefetch_related(self.def_prefetch_queryset), order_id=order_instance.pk, return_cache_name=True)
        items = cache[0]
        cache_name = cache[1]
        product_configs = []
        for item in items:
            is_purchased = item.sku_no.is_purchased
            if is_purchased:
                product_configs.append(item.product_config_id)
        if product_configs:
            self.pending_product_stock = ProductStocks.objects.filter(product_config_id__in=product_configs, is_purchased=False, is_pending=False)
        for item in items:
            sku_no = item.sku_no
            product_config_id = sku_no.product_config_id.pk
            is_purchased = sku_no.is_purchased
            if is_purchased:
                item.update(sku_no=self.return_random_stock(product_config_id))
        items.update(**fields)
        items.reload_from_db()
        super().delete_cache(cache_name=cache_name)
        return True

    def destroy(self, request, pk=None):
        order_instance = self.parent_model.objects.get(pk=pk)
        order_instance.delete()
        return Response({'message': 'deleted order on cancellation'}, status=status.HTTP_202_ACCEPTED)

class RepairsViewSet(custom_mixins.CommunicationViewSetMixin, custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    
    parent_serializer = auth_model_serializers.RepairsSerializer
    parent_model = auth_models.Repairs
    parent_id_field = 'repair_id'

    history_serializer = auth_model_serializers.RepairHistorySerializer
    history_model = auth_models.RepairHistory

    comm_history_serializer = auth_model_serializers.RepairCommunicationHistorySerializer
    comm_history_model = auth_models.RepairCommunicationHistory

    custom_actions = ['render_conf']

    cache_list_fields = [parent_model, 'user_id']
    cache_retreive_fields = [parent_model, parent_id_field]

    def list(self, request):
        queryset = super().list_cache(queryset=self.parent_model.objects, user_id=request.user.user_id)
        serializer = self.parent_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        repair_serializer_dict = {}
        repair_queryset = super().retrieve_cache(queryset=self.parent_model.objects, repair_id=pk)
        if repair_queryset is not None:
            self.check_object_permissions(request, repair_queryset)
            repair_serializer = self.parent_serializer(repair_queryset)
            repair_serializer_dict.update(**{'repair_details': repair_serializer.data})
        repair_history_queryset = self.history_model.filter(repair_id=pk)
        if repair_history_queryset is not None:
            repair_history_serializer = self.history_serializer(repair_history_queryset, many=True)
            repair_serializer_dict.update(**{'repair_history': repair_history_serializer.data})
        if is_admin_req:
            return repair_serializer_dict
        else:
            return Response(repair_serializer_dict, status=status.HTTP_200_OK)

    # @action(detail=True)
    def render_conf(self, request):
        repair_instance = kwargs.get('instance', None)
        if repair_instance is not None:
            repair_instance = self.parent_serializer(repair_instance)
            data = repair_instance.data
            return {'repair_details': data}

    def send_conf(self, request, **kwargs):
        return super().send_conf(request, **kwargs)

    def update_status(self, request, **kwargs):
        return super().update_status(request, **kwargs)

    def create(self, request, **kwargs):
        inital = kwargs.get('initial', None)
        if inital is not None:
            checkout_total = initial.get('checkout_total')
            data = {
                'user_id': request.user.user_id,
                'repair_date': datetime.date.today(),
                'product_id': initial['checkout_item_id'],
                'reason_repair': request.data.get('reason_repair', None),
                'error_codes': request.data.get('error_codes', None),
                'shipping_address_id': initial.get('shipping_address_id', None),
                'shipping_method_id': initial.get('shipping_method_id'),
                'shipping_price_excl': checkout_total['shipping'],
                'shipping_price_tax': checkout_total['vat'],
                'shipping_price_incl': checkout_total['total'],
                'is_cancelled': False,
                'is_completed': False,
                'current_status_id': 1,
                'current_status_date': datetime.date.today()
            }
            serializer = self.parent_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                repair_instance = serializer.save()
                request.session['repair_instance'] = repair_instance
                repair_instance = self.parent_model.objects.select_related('product_id').filter(pk=repair_instance['repair_id']).first()
                if repair_instance is not None:
                    super().list_cache(user_id=request.user.user_id, delete=True)
                    return repair_instance
                else:
                    raise custom_exceptions.not_found_error('repair')

    def update(self, request, **kwargs):
        repair_instance = kwargs.get('repair_instance')
        initial = kwargs.get('initial', None)
        if initial is not None:
            checkout_total = initial.get('checkout_total')
            data = {
                'reason_repair': request.data.get('reason_repair', None),
                'error_codes': request.data.get('error_codes', None),
                'shipping_address_id': initial.get('shipping_address_id', None),
                'shipping_method_id': initial.get('shipping_method_id'),
                'shipping_price_excl': checkout_total['shipping'],
                'shipping_price_tax': checkout_total['vat'],
                'shipping_price_incl': checkout_total['total'],
            }
            repair_instance.update(**data)
            repair_instance.reload_from_db()
            return repair_instance

class Checkout(OrdersViewSet, RepairsViewSet, ShoppingCartViewSet, external_api_views.PayfastIntegration, external_api_views.BobGoIntegration, custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    lookup_field = 'instance_type'
    lookup_url_kwargs = 'instance_type'

    permission_classes = [permissions.IsAuthenticated]
    checkout_instance_type = None
    checkout_instance_super = None
    checkout_instance_model = None
    checkout_instance_serializer = None
    # checkout_instance_id_field = None
    checkout_instance_id = None
    checkout_instance = None
    checkout_backend_load = False
    checkout_on_load = False
    checkout_instance_user_details = None
    checkout_user_address = None
    checkout_items = None
    checkout_saved_instance = False
    # ex_api_instance_type = checkout_instance_type
    # ex_api_instance_model = checkout_instance_model
    # ex_api_instance_serializer = checkout_instance_serializer
    # ex_api_instance_id_field = checkout_instance_id_field
    # ex_api_instance_id = checkout_instance_id
    # ex_api_instance = checkout_instance
    # ex_api_instance_user_details = checkout_instance_user_details
    # ex_api_user_address = checkout_user_address
    # ex_api_user_address_instance = None

    # @action(detail=False, methods=['post'])
    def initialize_new(self, request, instance_type=None):
        '''
        get checkout type from client, get checkout items, initalize model, serializer and ID field associated
        '''
        checkout_type = instance_type
        if checkout_type is not None:
            self.initialize(checkout_type)
            if checkout_type == 'repair':
                product_id = request.query_params.get('product_id', None)
                if product_id is not None:
                    product_instance = st_models.Products.get(pk=product_id)
                    if product_instance.is_active == False:
                        raise custom_exceptions.item_non_active_error('product')
                    else:
                        self.checkout_items = product_instance
                else:
                    raise custom_exceptions.invalid_or_none_error('product_id')
            if checkout_type == 'order':
                super(RepairsViewSet, self).list(request, backend_req=True)
                self.checkout_items = self.shopping_cart_items_obj
            else:
                raise custom_exceptions.invalid_type_error('checkout')
        else:
            raise custom_exceptions.none_not_allowed_error('checkout type')

    def initialize(self, instance_type):
        self.checkout_instance_type = instance_type
        if instance_type == 'repair':
            self.checkout_instance_super = super(OrdersViewSet, self)
        if instance_type == 'order':
            self.checkout_instance_super = super()
        else:
            raise custom_exceptions.invalid_type_error('checkout')
        self.checkout_instance_model = getattr(self.checkout_instance_super, 'parent_model')
        self.checkout_instance_serializer = getattr(self.checkout_instance_super, 'parent_serializer')
        self.checkout_id_field = getattr(self.checkout_instance_super, 'parent_id_field')
        return True

    def initialize_saved(self, instance):
        self.checkout_instance = instance
        self.checkout_instance_id = instance.pk

    @action(detail=False, methods=['post'])
    def get_shipping_method(self, request, **kwargs):
        shipping_method_id = request.data.get('shipping_method_id', self.checkout_instance.shipping_method_id)
        shipping_address_id = request.data.get('shipping_address_id', self.checkout_instance.shipping_address_id)
        request.session['shipping_method_id'] = shipping_method_id
        if shipping_method_id == 1:
            if self.checkout_user_address is None:
                if shipping_address_id is None:
                    default_address_id = self.checkout_instance_user_details.default_address_id
                    if default_address_id is None:
                        shipping_address_id = None
                    else:
                        shipping_address_id = default_address_id
                if shipping_address_id is not None:
                    try:
                        fields = {'user_id': request.user.user_id}
                        queryset = super().get_or_set(model='user_addresses', extra_fields=fields, queryset=reg_models.UserAddresses.objects)
                        user_address_obj = super().filter_cache(queryset, fields={'address_id': shipping_address_id})
                    except SomeModel.DoesNotExist:
                        user_address_obj = None
                    if user_address_obj is not None:
                        serializer = reg_model_serializers.UserAddressSerializer(user_address_obj)
                        self.checkout_user_address = serializer.data
                        data = super().get_checkout_rate(request)
                else:
                    data = 0
            else:
                data = super().get_checkout_rate(request)
        else:
            data = 0
        if self.checkout_backend_load:
            data = {
                'checkout_shipping_rate': data, 
                'shipping_method_id': shipping_method_id
            }
            if self.checkout_user_address is not None:
                data.append(**{'shipping_address_id': self.checkout_user_address['address_id']})
            return data
        if data > 0:
            if self.checkout_on_load:
                return {'checkout_shipping_rate': data}
            self.calculate_total(request, checkout_shipping_rate=data)

    def calculate_product_vat(self):
        if self.checkout_items is not None:
            for item in self.checkout_items:
                price = item.sku_no.product_config_id.price
                vat = round((price * vat_perc), 2)
                data = {
                    'order_item_excl': price,
                    'order_item_vat': vat,
                    'order_item_incl': price + vat
                }
                item.update(data)
                item.reload_from_db()
        return True

    @action(detail=False)
    def calculate_total(self, request, **kwargs):
        '''
        calculate total incl shipping
        note: 
        - if not on saved checkout:
        product calculations for VAT are not redone, rather, they are taken from the shopping cart viewset
        - else:
        product calculations are redone to match the product config price
        '''
        checkout_shipping_rate = kwargs.get('checkout_shipping_rate', 0)
        if self.checkout_saved_instance:
            total_quantity = self.checkout_items.count()
            subtotal_excl = 0
            if self.checkout_instance == 'order':
                for item in self.checkout_items:
                    subtotal_excl += item.order_item_excl
        else:
            if self.checkout_items is not None:
                if self.checkout_instance_type == 'order':
                    shopping_cart_items_obj = super().shopping_cart_items_obj
                    subtotal_excl = shopping_cart_items_obj.subtotal
                    total_quantity = shopping_cart_items_obj.total_quantity
                if self.checkout_instance_type == 'repair':
                    subtotal_excl = 0
                    total_quantity = 0
        shipping_vat = round((checkout_shipping_rate * vat_perc), 2)
        shipping = checkout_shipping_rate + shipping_vat
        subtotal_incl = subtotal_excl + shipping
        vat = round((subtotal_incl * vat_perc), 2)
        total = vat + subtotal_incl
        data = {
            'total_quantity': total_quantity,
            'subtotal_excl': subtotal_excl,
            'shipping': shipping,
            'subtotal_incl': subtotal_incl,
            'vat': vat,
            'total': total
        }
        if self.checkout_on_load or self.checkout_backend_load:
            return data
        else:
            return Response(data, status=status.HTTP_200_OK)

    @action(detail=False)
    def contains_exchange_unit(self, request, **kwargs):
        '''
        check if checkout items contains exchange unit
        '''
        if self.checkout_items is not None:
            contains_ex = False
            for item in self.checkout_items:
                if self.checkout_saved_instance:
                    product_config = item.sku_no.product_config_id
                else:
                    product_config = item.product_config_id
                if product_config.variation_id == 2:
                    contains_ex = True
                    break
            return contains_ex

    def initialize_user_addresses(self, request):
        fields = {'user_id': request.user.user_id}
        queryset = super().get_or_set(model='user_addresses', extra_fields=fields, queryset=reg_models.UserAddresses.objects)
        serializer = UserAddressesSerializer(queryset, many=True)
        return serializer.data

    def initialize_user(self, request):
        '''
        initializes user details, from queryset or cache
        '''
        fields = {'user_id': request.user.user_id}
        queryset = super().get_or_set(model='user_details', extra_fields=fields, queryset=reg_models.UserDetails.objects)
        self.checkout_instance_user_details = queryset

    def serialized_checkout_items(self):
        '''
        returns serialized versions of products
        '''
        if self.checkout_instance_type == 'order':
            if self.checkout_saved_instance:
                super().retrieve_items(request, pk=self.checkout_instance_id)
            else:
                data = super().serialized_response(backend_req=True, exclude='shopping_cart')
        if self.checkout_instance_type == 'repair':
            serializer = st_model_serializers.ProductsSerializer(self.checkout_items)
            data = serializer.data
        return data

    def check_active(self, **kwargs):
        if self.checkout_instance_type == 'repair':
            items = [self.checkout_items]
        else:
            items = self.checkout_items
        for item in items:
            if self.checkout_instance_type == 'order':
                if self.checkout_saved_instance:
                    product_config_id = item.sku_no.product_config_id
                    product_id = product_config_id.product_id
                else:
                    product_config_id = item.product_config_id
                    product_id = item.product_config_id.products_id
                quantity = [i for i in items if i.product_config_id == product_config_id].count()
                if (product_config_id.stock_available - 2) > quantity:
                    return Exception
            else:
                product_id = item
            if product_id.is_active == False:
                return custom_exceptions.item_non_active_error('product')
        return True

    def run_checks(self, request, instance_type=None, pk=None):
        '''
        used for the retrieve() and payment_initialize_data() methods
        '''
        self.initialize_user(request)
        if self.checkout_saved_instance:
            if self.checkout_backend_load():
                self.continue_saved_checkout(request, pk=pk, instance_type=instance_type)
        else:
            self.initialize_new(request, instance_type=instance_type)
        shipping_rate = self.get_shipping_method(request)
        checkout_total = self.calculate_total(request, **shipping_rate)
        data = {
            'checkout_total': checkout_total
        }
        self.check_active()
        if self.checkout_instance_type == 'order':
            data['checkout_contains_ex'] = self.contains_exchange_unit()
        if self.checkout_on_load:
            data['checkout_items'] = self.serialized_checkout_items()
            data['user_addresses'] = self.initialize_user_addresses(request)
            data['active_address'] = self.checkout_user_address
        if self.checkout_backend_load:
            shipping_rate.pop('checkout_shipping_rate', '')
            data.append(**shipping_rate)
            if self.checkout_instance_type == 'repair':
                data['checkout_item_id'] = self.checkout_items.pk
        return data

    def retrieve(self, request, instance_type=None, **kwargs):
        '''
        return initial values on page load
        '''
        self.checkout_on_load = True
        data = self.run_checks(request, instance_type=instance_type)
        extra_vals = kwargs.get('extra_vals', None)
        if extra_vals is not None:
            data.append(**extra_vals)
        self.checkout_on_load = False
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path=r'(?P<pk>\d+)/initialize')
    def payment_initialize_data(self, request, instance_type=None, pk=None):
        ''' 
        initialize data process for payfast, including running checks and creating instance
        '''
        self.checkout_backend_load = True
        data = self.run_checks(request, instance_type=instance_type, pk=pk)
        initial = {'initial': data}
        if self.checkout_saved_instance:
            initial.append(**{f'{self.checkout_instance_type}': self.checkout_instance})
            action = 'update'
        else:
            action = 'create'
        instance = getattr(self.checkout_instance_super, action)
        self.initialize_saved(instance(request, **initial))
        if self.checkout_instance_type == 'order':
            if action == 'create':
                self.create_order_items(request, initial_data_items=self.checkout_items, order_instance=self.checkout_instance)
            else:
                self.update_order_items(request, fields={'is_pending': True}, order_instance=self.checkout_instance)
            if order_instance.contains_ex == True:
                update_or_delete_ex_images(request, order_instance=order_instance)
        self.checkout_backend_load = False
        return super().initialize_form(request)

    @action(detail=True, methods=['get'], url_path=r'(?P<pk>\d+)')
    def continue_saved_checkout(self, request, pk=None, instance_type=None):
        if pk is not None:
            self.checkout_saved_instance = True
            self.initialize(instance_type=instance_type)
            self.initialize_saved(self.checkout_instance_model.objects.get(pk=pk))
            if instance_type == 'order':
                child_model = getattr(self.checkout_instance_super, 'child_model')
                prefetch_qs = getattr(self.checkout_instance_super, 'def_prefetch_queryset')
                self.checkout_items = child_model.objects.prefetch_related(prefetch_qs).filter(order_id=pk)
            if instance_type == 'repair':
                self.checkout_items = self.checkout_instance.product_id
                extra_vals = {'saved_reason_repair': self.checkout_instance.reason_repair, 'saved_error_codes': self.checkout_instance.error_codes}
            return self.retrieve(request, instance_type=instance_type, extra_vals=extra_vals)

    @action(detail=False, methods=['get'], url_path=r'(?P<pk>\d+)/cancel')
    def payment_cancel(self, request, pk=None):
        '''
        if pk matches, sets instance (and items) to 'saved'
        '''
        if self.checkout_instance_id == pk:
            current_status_id = {'current_status_id': 3,}
            fields = {
                **current_status_id,
                'current_status_date': date,
            }
            status_data = {
                **current_status_id,
                'subject': f'Your {self.checkout_instance_type} {self.checkout_instance_id} has been saved for future payment',
                'comment': '',
                'instance': self.checkout_instance,
                'comm_method': ''
            }
            update_status = getattr(self.checkout_instance_super, 'update_status')
            update_status(request, **status_data)
            if self.checkout_instance_type == 'order':
                self.update_order_items(request, pk=self.checkout_instance_id, fields=fields)
            return Response({'message': f'successfully saved {self.checkout_instance_type}'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'], url_path=r'(?P<pk>\d+)/recieve')
    def payment_recieve_data(self, request, pk=None):
        '''
        if pk matches, recieve data
        '''
        if self.checkout_instance_id == pk:
            return super().recieve_data(request)

    @action(detail=False, url_path=r'(?P<pk>\d+)/render-conf')
    def render_conf(self, request, pk=None):
        '''
        process data through payfast security checks with conduct_security_checks()
        if successful, continue process
        render and serialize data in render_conf(), return to user
        if shipping_method_id '1' was selected, create shipment from BobGo API
        pass serialized data to send_conf()
        send confirmed status using update_status()

        will send a response to the client in the instance the security checks weren't successful for the admin/technical department to investigate

        '''
        if self.checkout_instance_id == pk:
            super().conduct_security_checks(request)
            if True:
                html_conf = getattr(self.checkout_instance_super, 'render_conf')
                data = html_conf(request, instance=self.checkout_instance, user_details=self.checkout_instance_user_details)
                if self.checkout_instance.shipping_method_id == 1:
                    super().create_shipment(request)
                    self.checkout_instance.refresh_from_db()
                subject = f'Your {self.checkout_instance_type} {self.checkout_instance_id} is confirmed'
                comment = subject
                status_data = {
                    'subject': subject,
                    'comment': comment,
                    'instance': self.checkout_instance,
                    'comm_method': 'SMS, email'
                }
                conf_data = status_data
                conf_data.pop('comm_method')
                conf_data.append(**{'serializer_data': data})
                send_conf = getattr(self.checkout_instance_super, 'send_conf')
                update_status = getattr(self.checkout_instance_super, 'update_status')
                if self.checkout_instance_type == 'order':
                    status_data['current_status_id'] = 1
                if self.checkout_instance_type == 'repair':
                    status_data['current_status_id'] = 2
                send_conf(request, **conf_data)
                update_status(request, **status_data)
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid Checkout Instance ID'}, status=status.HTTP_400_BAD_REQUEST)

class ReturnsViewSet(custom_mixins.CommunicationViewSetMixin, custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]
    
    def_prefetch_queryset = Prefetch('order_item_id__sku_no__product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id'))

    parent_serializer = auth_model_serializers.ReturnsSerializer
    parent_serializer_ex = auth_serializers.ReturnsSerializerEx
    parent_model = auth_models.Returns
    parent_id_field = 'return_id'

    history_serializer = auth_model_serializers.ReturnHistorySerializer
    history_model = auth_models.ReturnHistory
    
    comm_history_serializer = auth_model_serializers.ReturnCommunicationHistorySerializer
    comm_history_model = auth_models.ReturnCommunicationHistory

    cache_list_fields = [parent_model, 'user_id']
    cache_retrieve_fields = [parent_model, parent_id_field]

    def list(self, request):
        queryset = super().list_cache(queryset=self.parent_model.objects, user_id=request.user.user_id)
        serializer = self.parent_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        return_serializer_dict = {}
        return_queryset = order_queryset = super().retrieve_cache(queryset=self.parent_model.objects, return_id=pk)
        if return_queryset is not None:
            self.check_object_permissions(request, return_queryset)
            return_serializer = self.parent_serializer(return_queryset)
            return_serializer_dict.update(**{'return_details': return_serializer.data})
        return_history_queryset = self.history_model.objects.filter(return_id=pk)
        if return_history_queryset is not None:
            return_history_serializer = self.history_serializer(return_history_queryset, many=True)
            return_serializer_dict.update(**{'return_history': return_history_serializer.data})
        if is_admin_req:
            return return_serializer_dict
        else:
            return Response(return_serializer_dict, status=status.HTTP_200_OK)

    def send_conf(self, request, **kwargs):
        return_instance = kwargs.get('return_instance', None)
        if return_instance is not None:
            return_serializer = self.parent_serializer(return_instance)
            serializer_data = {'return_details': return_serializer.data}
            comm_object_data = {
                'type_id': return_instance.return_id,
                'serializer_data': serializer_data,
                'subject': kwargs.get('subject', None),
                'comment': kwargs.get('comment', None)
            }
            return super().send_conf(request, **comm_object_data)

    def update_status(self, request, **kwargs):
        return super().update_status(request, **kwargs)

    def create(self, request):
        default = {
            'user_id': request.user.user_id,
            'return_date': datetime.datetime.now(),
            'is_completed': False,
            'current_status_id': 2,
            'current_status_date': custom_utils.return_date_and_time()
        }
        serializer = auth_model_serializers.ReturnsSerializer(data=request.data, context=default)
        if serializer.is_valid(raise_exception=True):
            return_instance = serializer.save()
            request.session['return_instance'] = return_instance
            return_instance = auth_models.Returns.objects.prefetch_related(self.def_prefetch_queryset).select_related('order_id').filter(pk=return_instance['repair_id']).first()
            super().list_cache(user_id=request.user.user_id, delete=True)
            return self.send_return_conf(request, return_instance=return_instance)