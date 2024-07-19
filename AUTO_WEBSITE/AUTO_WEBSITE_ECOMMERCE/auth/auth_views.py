from rest_framework import viewsets, status, views, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from . import auth_models, auth_model_serializers, auth_serializers, auth_utils, auth_permissions, auth_mixins
from .. import serializers as custom_serializers, utils as custom_utils, mixins as custom_mixins, exceptions as custom_exceptions
from django.http import Http404
from django.conf import settings
from ..reg.reg_model_serializers import UserAddressesSerializer
from ..reg import reg_models
from ..standard import st_models, st_model_serializers
from ..external_api import external_api_views
import re, random, datetime, logging, json
from decimal import Decimal as dec
from django.db.models import Prefetch, F
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

sage = external_api_views.SageAccountingIntegration
vat_perc = dec(0.15)
logger = logging.getLogger(__name__)

class ShoppingCartViewSet(custom_mixins.TempMixin, viewsets.ViewSet):
    permission_classes = [auth_permissions.BaseAuthUserPermission]

    __parent_serializer = auth_model_serializers.ShoppingCartSerializer
    __child_serializer = auth_model_serializers.ShoppingCartItemsSerializer
    __child_serializer_ex = auth_serializers.ShoppingCartItemsSerializerEx

    __parent_model = auth_models.ShoppingCart
    __child_model = auth_models.ShoppingCartItems

    temp_name = 'shopping_cart_obj'

    def __create_shopping_cart(self, request):
        user = request.user
        shopping_cart_obj = self.__parent_model.objects.create(user_id=user)
        return True

    def serialized_response(self, request, pk=None, **kwargs):
        '''
        serialized shopping cart data, for responses ONLY

        -> is defined as a seperate function for queryset-only use cases (for the ShoppingCartViewSet and Checkout)
        '''
        data = {}
        backend_req = kwargs.get('backend_req', False)
        exclude = kwargs.get('exclude', None)
        temp = kwargs.get('temp', None)
        flag = kwargs.get('flag', None)
        item = kwargs.get('item', None)
        if temp is not None:
            request.method = 'GET'
            if temp.shopping_cart_obj is not None:
                serializer1 = self.__parent_serializer(temp.shopping_cart_obj)
                data.update(**{'shopping_cart': serializer1.data})
                context = {'request': request}
                if item is not None:
                    serializer2 = self.__child_serializer(item, context=context)
                else:
                    if temp.shopping_cart_items_obj is not None:
                        serializer2 = self.__child_serializer(temp.shopping_cart_items_obj, many=True, context=context)
                data.update(**{'shopping_cart_items': serializer2.data})
                if exclude is not None:
                    data.pop(exclude, '')
                if flag is not None:
                    data.update(**{'flag': flag})
                print(data)
                if backend_req:
                    return data
                else:
                    return Response(data, status=status.HTTP_200_OK)

    def items_load(self, temp):
        if temp.shopping_cart_obj is not None:
            prefetch_query = Prefetch('product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id').filter(product_id__is_active=True))
            shopping_cart_items_obj = self.__child_model.objects.prefetch_related(prefetch_query).filter(shopping_cart_id=temp.shopping_cart_obj.pk)
            shopping_cart_items_list = []
            if not shopping_cart_items_obj:
                shopping_cart_items_list = None
            else:
                for item in shopping_cart_items_obj:
                    shopping_cart_items_list.append(item)
            temp.shopping_cart_items_obj = shopping_cart_items_list

    def list(self, request, backend_req=False, **kwargs):
        user = request.user
        try:
            shopping_cart_obj = self.__parent_model.objects.get(user_id=user.user_id)
            temp = kwargs.get('temp', super().init_temp(request))
            temp.shopping_cart_obj = shopping_cart_obj
            self.items_load(temp)
            super().set_temp(request, temp)
            if not backend_req:
                return self.serialized_response(request, temp=temp)
        except self.__parent_model.DoesNotExist:
            self.__create_shopping_cart(request)
            if True:
                self.list(request)

    def check_quantity(self, **kwargs):
        obj = kwargs.get('obj', None)
        pk = kwargs.get('pk', None)
        if obj is None:
            if pk is not None:
                obj = st_models.Products.objects.get(pk=pk)
        if obj is not None:
            return obj.product_config_id.has_stock

    def update(self, request, **kwargs):
        temp = kwargs.get('temp', None)
        if temp is not None:
            if temp.shopping_cart_obj is not None:
                shopping_cart_items_cal = []
                total_quantity = 0
                subtotal = 0
                if temp.shopping_cart_items_obj is not None:
                    for item in temp.shopping_cart_items_obj:
                        total_quantity += item.quantity
                        subtotal += item.total_price
                subtotal = dec(subtotal)
                vat = round((subtotal * vat_perc), 2)
                total = subtotal + vat
                shopping_cart_total_dict = {
                    'total_quantity': total_quantity,
                    'subtotal': subtotal,
                    'vat': vat,
                    'total': total
                }
                for key, value in shopping_cart_total_dict.items():
                    setattr(temp.shopping_cart_obj, key, value)
                temp.shopping_cart_obj.save()
                temp.shopping_cart_obj.refresh_from_db()
                super().set_temp(request, temp)

    def partial_update(self, request, pk=None, **kwargs):
        backend_req = kwargs.get('backend_req', False)
        if backend_req:
            temp = kwargs.get('temp', None)
            quantity = kwargs.get('quantity', None)
            obj = kwargs.get('obj', None)
            total_price = kwargs.get('total_price', None)
        else:
            quantity = request.data.get('quantity', None)
            temp = super().get_temp(request)
            if temp is not None:
                if temp.shopping_cart_items_obj is not None:
                    for item in temp.shopping_cart_items_obj:
                        if int(pk) == item.pk:
                            obj = item
        if obj is not None:
            obj.quantity = int(quantity)
            obj.total_price = dec(obj.quantity) * obj.product_config_id.price
        check_quantity = self.check_quantity(obj=obj)
        if check_quantity:
            obj.save()
            self.update(request, temp=temp)
            return self.serialized_response(request, temp=temp, item=obj, flag='updated')
        else:
            return Response({'message': 'not enough stock!'}, status=status.HTTP_400_BAD_REQUEST)

    def __internal_create(self, request, **kwargs):
        serializer = kwargs.get('serializer', None)
        temp = kwargs.get('temp', None)
        if serializer is not None:
            item = serializer.save()
            item = self.__child_model.objects.select_related('product_config_id__product_id', 'product_config_id__variation_id').filter(pk=item.pk)[0]
            if temp.shopping_cart_items_obj is not None:
                temp.shopping_cart_items_obj.append(item)
            else:
                temp.shopping_cart_items_obj = [item]
            self.update(request, temp=temp)
            return self.serialized_response(request, temp=temp, item=item, flag='created')

    def create(self, request):
        temp = super().get_temp(request)
        print(temp.shopping_cart_obj)
        if temp.shopping_cart_obj is not None:
            data = request.data
            quantity = data['quantity']
            product_price = st_models.ProductConfig.objects.get(pk=data['product_config_id']).price
            total_price = product_price * dec(quantity)
            data['total_price'] = total_price
            data['shopping_cart_id'] = temp.shopping_cart_obj.pk
            data['user_id'] = request.user.user_id
            serializer = self.__child_serializer(data=data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                print(data)
                if temp.shopping_cart_items_obj is not None:
                    for item in temp.shopping_cart_items_obj:
                        if item.product_config_id == data['product_config_id']:
                            return self.partial_update(request, obj=item, backend_req=True, quantity=quantity, total_price=total_price, temp=temp)
                return self.__internal_create(request, serializer=serializer, temp=temp)
        else:
            self.__create_shopping_cart(request)
            if True:
                self.create(request)

    def destroy(self, request, pk=None):
        temp = super().get_temp(request)
        if temp is not None:
            if temp.shopping_cart_obj is not None:
                if temp.shopping_cart_items_obj is not None:
                    for item in temp.shopping_cart_items_obj:
                        if item.pk == int(pk):
                            item.delete()
                            temp.shopping_cart_items_obj.remove(item)
                            self.update(request, temp=temp)
                            return self.serialized_response(request, temp=temp)

class InvoicesViewSet(custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]

    __parent_serializer = auth_model_serializers.InvoicesSerializer
    __child_serializer = auth_model_serializers.InvoiceItemsSerializer

    __parent_model = auth_models.Invoices
    __parent_id_field = 'invoice_id'
    __child_model = auth_models.InvoiceItems
    child_id_field = 'invoice_item_id'

    cache_list_fields = ['parent_model', 'user_id']
    cache_retreive_fields = ['parent_model', 'parent_id_field']

    # def_prefetch_queryset = Prefetch('order_item_id__sku_no__product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id'))

    def get_private(self, attrs):
        return custom_utils.get_private(self=self, attrs=attrs)

    def list(self, request):
        data = self.__parent_model.objects.filter(user_id=request.user.user_id)
        serializer = self.__parent_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, **kwargs):
        is_admin_req = kwargs.get('is_admin_req', False)
        invoice_serializer_dict = {}
        invoice_queryset = self.__parent_model.objects.select_related().filter(pk=pk).first()
        if invoice_queryset is not None:
            self.check_object_permissions(request, invoice_queryset)
            invoice_serializer = self.__parent_serializer(invoice_queryset)
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
            invoice_serializer = self.__parent_serializer(data=data)
            if invoice_serializer.is_valid(raise_exception=True):
                invoice_instance = invoice_serializer.save()
                invoice_instance = self.__parent_models.objects.get(pk=invoice_instance['invoice_id'])
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
            invoice_item_serializer = self.__child_serializer(data=invoice_item_data, many=True)
            if invoice_item_serializer.is_valid(raise_exception=True):
                invoice_item_serializer.save()
                return True

class OrdersViewSet(InvoicesViewSet, custom_mixins.CommunicationViewSetMixin, custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]

    def_prefetch_queryset = Prefetch('sku_no__product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id'))

    __parent_serializer = auth_model_serializers.OrdersSerializer
    # parent_serializer_ex = auth_serializers.OrdersSerializerEx
    __child_serializer = auth_model_serializers.OrderItemsSerializer
    __child_serializer_ex = auth_serializers.OrderItemsSerializerEx
    __file_serializer = auth_model_serializers.OrderExUnitImagesSerializer

    __parent_model = auth_models.Orders
    __parent_id_field = 'order_id'
    __child_model = auth_models.OrderItems
    __child_id_field = 'order_item_id'
    __file_model = auth_models.OrderExUnitImages
    __file_id_field = 'order_ex_unit_filename'

    cache_field = 'user_id'

    history_serializer = auth_model_serializers.OrderHistorySerializer
    history_model = auth_models.OrderHistory

    comm_history_serializer = auth_model_serializers.OrderCommunicationHistorySerializer
    comm_history_model = auth_models.OrderCommunicationHistory

    __obj_type = 'order'

    is_admin_req = False

    custom_actions = ['render_conf']

    cache_list_fields = ['parent_model', 'user_id']
    cache_retreive_fields = ['parent_model', 'parent_id_field']
    cache_retreive_child_fields = ['child_model', 'parent_id_field']

    pending_product_stock = None

    def get_private(self, attrs):
        return custom_utils.get_private(self=self, attrs=attrs)

    def list(self, request):
        queryset = super().list_cache(queryset=self.__parent_model.objects, user_id=request.user.user_id, extra_fields=request.query_params)
        serializer = self.__parent_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    # @action(detail=True)
    def render_conf(self, request):
        order_instance = kwargs.get('instance', None)
        if order_instance is not None:
            order_instance = self.__parent_serializer(order_instance)
            cache = super().get_or_set(queryset=self.__child_model.objects.prefetch_related(self.def_prefetch_queryset), order_id=order_instance.pk, return_cache_name=True)
            order_items_instance = cache[0]
            order_items_serializer = self.__child_serializer(order_items_instance, many=True)
            invoice_download_link = super().create_invoice(request, order_instance=order_instance, order_items_instance=order_items_instance, order_user_details=kwargs.get('user_details'))
            data = {'order_details': order_instance.data, 'order_items': order_items_serializer.data, 'invoice_download_link': invoice_download_link}
            return data

    def retrieve(self, request, pk=None):
        order_serializer_dict = {}
        order_queryset = super().retrieve_cache(queryset=self.__parent_model.objects, order_id=pk)
        if order_queryset is not None:
            self.check_object_permissions(request, order_queryset)
            order_serializer = self.__parent_serializer(order_queryset)
            order_serializer_dict.update(**{'order_details': order_serializer.data})
            order_item_serializer = self.retrieve_items(request, pk=pk)
            order_serializer_dict.update(**{'order_items': order_item_serializer.data})
            order_history_queryset = self.__history_model.objects.filter(order_id=pk)
            if order_history_queryset is not None:
                order_history_serializer = self.__history_serializer(order_history_queryset, many=True)
                order_serializer_dict.update(**{'order_history': order_history_serializer.data})
        if is_admin_req:
            return order_serializer_dict
        else:
            return Response(order_serializer_dict, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def retrieve_items(self, request, pk=None):
        order_items_queryset = super().get_or_set(queryset=self.__child_model.objects.prefetch_related(self.def_prefetch_queryset), order_id=pk)
        if order_items_queryset is not None:
            return self.__child_serializer(order_items_queryset, many=True)

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
            serializer = self.__parent_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                order_instance = serializer.save()
                order_instance = self.__parent_model.objects.select_related('shipping_method_id', 'shipping_address_id').filter(pk=order_instance['order_id']).first()
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
            serializer = self.__file_serializer(data=data, many=True)
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
        serializer = self.__child_serializer(data=order_item_list_data, many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            super().list_cache(user_id=request.user.user_id, delete=True)
            return True

    def update_order_items(self, request, **kwargs):
        fields = kwargs.get('fields', None)
        order_instance = kwargs.get('order_instance')
        cache = super().get_or_set(queryset=self.__child_model.objects.prefetch_related(self.def_prefetch_queryset), order_id=order_instance.pk, return_cache_name=True)
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
        order_instance = self.__parent_model.objects.get(pk=pk)
        order_instance.delete()
        return Response({'message': 'deleted order on cancellation'}, status=status.HTTP_202_ACCEPTED)

class RepairsViewSet(custom_mixins.CommunicationViewSetMixin, custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    
    __parent_serializer = auth_model_serializers.RepairsSerializer
    __parent_model = auth_models.Repairs
    __parent_id_field = 'repair_id'

    __history_serializer = auth_model_serializers.RepairHistorySerializer
    __history_model = auth_models.RepairHistory

    __comm_history_serializer = auth_model_serializers.RepairCommunicationHistorySerializer
    __comm_history_model = auth_models.RepairCommunicationHistory

    __obj_type = 'repair'

    custom_actions = ['render_conf']

    cache_list_fields = ['parent_model', 'user_id']
    cache_retreive_fields = ['parent_model', 'parent_id_field']

    def get_private(self, attrs):
        return custom_utils.get_private(self=self, attrs=attrs)

    def list(self, request):
        queryset = super().list_cache(queryset=self.__parent_model.objects, user_id=request.user.user_id)
        serializer = self.__parent_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        repair_serializer_dict = {}
        repair_queryset = super().retrieve_cache(queryset=self.__parent_model.objects, repair_id=pk)
        if repair_queryset is not None:
            self.check_object_permissions(request, repair_queryset)
            repair_serializer = self.__parent_serializer(repair_queryset)
            repair_serializer_dict.update(**{'repair_details': repair_serializer.data})
        repair_history_queryset = self.__history_model.filter(repair_id=pk)
        if repair_history_queryset is not None:
            repair_history_serializer = self.__history_serializer(repair_history_queryset, many=True)
            repair_serializer_dict.update(**{'repair_history': repair_history_serializer.data})
        if is_admin_req:
            return repair_serializer_dict
        else:
            return Response(repair_serializer_dict, status=status.HTTP_200_OK)

    # @action(detail=True)
    def render_conf(self, request):
        repair_instance = kwargs.get('instance', None)
        if repair_instance is not None:
            repair_instance = self.__parent_serializer(repair_instance)
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
            serializer = self.__parent_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                repair_instance = serializer.save()
                request.session['repair_instance'] = repair_instance
                repair_instance = self.__parent_model.objects.select_related('product_id').filter(pk=repair_instance['repair_id']).first()
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

@method_decorator(never_cache, name='dispatch')
class Checkout(OrdersViewSet, RepairsViewSet, ShoppingCartViewSet, external_api_views.PayfastIntegration, external_api_views.BobGoIntegration, custom_mixins.DefaultCacheMixin, custom_mixins.TempMixin, viewsets.ViewSet):
    lookup_field = 'instance_type'
    lookup_url_kwargs = 'instance_type'

    permission_classes = [permissions.IsAuthenticated]
    # checkout_instance_type = None
    # checkout_instance_super = None
    # checkout_instance_model = None
    # checkout_instance_serializer = None
    # checkout_instance_id_field = None
    # checkout_instance_id = None
    # checkout_instance = None
    checkout_backend_load = False
    checkout_on_load = False
    # checkout_instance_user_details = None
    # checkout_user_address = None
    # checkout_items = None
    # checkout_saved_instance = False
    checkout_instance_super = None

    def __initialize_super(self, instance_type=None):
        if instance_type == 'repair':
            instance_super = [OrdersViewSet, self]
        if instance_type == 'order':
            instance_super = []
        self.checkout_instance_super = instance_super
        instance_class = globals()[f'{instance_type.capitalize()}sViewSet']
        return instance_class

    def initialize_new(self, request, instance_type=None, **kwargs):
        '''
        get checkout type from client, get checkout items, initalize model, serializer and ID field associated
        '''
        checkout_type = instance_type
        temp = kwargs.get('temp', None)
        if checkout_type is not None:
            self.initialize(checkout_type, temp=temp)
            if checkout_type == 'repair':
                product_id = request.query_params.get('product_id', None)
                if product_id is not None:
                    product_instance = st_models.Products.objects.get(pk=product_id)
                    if product_instance.is_active == False:
                        raise custom_exceptions.item_non_active_error('product')
                    else:
                        temp.checkout_items = [product_instance]
                else:
                    raise custom_exceptions.invalid_or_none_error('product_id')
            elif checkout_type == 'order':
                super(RepairsViewSet, self).list(request, backend_req=True)
                if temp.shopping_cart_items_obj is not None:
                    temp.checkout_items = temp.shopping_cart_items_obj
            else:
                raise custom_exceptions.invalid_type_error('checkout')
        else:
            raise custom_exceptions.none_not_allowed_error('checkout type')

    def initialize(self, instance_type, **kwargs):
        temp = kwargs.get('temp', None)
        if temp is not None:
            temp.checkout_instance_type = instance_type
            temp_view = self.__initialize_super(instance_type=temp.checkout_instance_type)()
            temp.checkout_instance_model, temp.checkout_instance_serializer, temp.checkout_id_field = temp_view.get_private(['parent_model', 'parent_serializer', 'parent_id_field'])
            return True

    def initialize_saved(self, instance, **kwargs):
        temp = kwargs.get('temp', None)
        if temp is not None:
            temp.checkout_instance = instance
            temp.checkout_instance_id = instance.pk

    def __get_user_address(self, request, **kwargs):
        temp = kwargs.get('temp', None)
        if temp is not None:
            checkout_instance = getattr(temp, 'checkout_instance', None)
            shipping_address_id = request.data.get('shipping_address_id', getattr(checkout_instance, 'shipping_address_id', None))
            if shipping_address_id is None:
                default_address_id = getattr(temp.checkout_instance_user_details, 'default_address_id', None)
                shipping_address_id = default_address_id
            if shipping_address_id is not None:
                try:
                    fields = {'user_id': request.user.user_id}
                    queryset = super().get_or_set(model='_user_addresses', extra_fields=fields, queryset=reg_models.UserAddresses.objects)
                    print(queryset)
                    user_address_obj = super().filter_cache(queryset, fields=[{'pk': shipping_address_id, 'data_type': 'int'}])[0]
                except Exception:
                    user_address_obj = None
                # if user_address_obj is not None:
                #     serializer = UserAddressesSerializer(user_address_obj)
                #     user_address_obj = serializer.data
                #     shipping_address_id = user_address_obj
                temp.checkout_user_address = user_address_obj
            data = {'shipping_address_id': getattr(temp.checkout_user_address, 'address_id', None)}
            return data

    @action(detail=False, methods=['post'])
    def get_shipping_method(self, request, **kwargs):
        temp = kwargs.get('temp', super().get_temp(request))
        checkout_instance = getattr(temp, 'checkout_instance', None)
        shipping_method_id = request.data.get('shipping_method_id', getattr(checkout_instance, 'shipping_method_id', None))
        print(shipping_method_id)
        request.session['shipping_method_id'] = shipping_method_id
        if temp is not None:
            data = {}
            if shipping_method_id is None:
                shipping_rate = 0
            else:
                if int(shipping_method_id) == 1:
                    shipping_address_id = self.__get_user_address(request, temp=temp)
                    data.update(**shipping_address_id)
                    shipping_rate = super().get_checkout_rate(request, temp=temp)
                else:
                    shipping_rate = 0
            data.update({
                'checkout_shipping_rate': dec(shipping_rate), 
                'shipping_method_id': shipping_method_id
            })
            if self.checkout_on_load or self.checkout_backend_load:
                if self.checkout_on_load:
                    data.pop('shipping_method_id', None)
                return data
            return self.calculate_total(request, checkout_shipping_rate=data.get('checkout_shipping_rate', 0), temp=temp)

    def calculate_product_vat(self, **kwargs):
        temp = kwargs.get('temp', None)
        if temp is not None:
            if temp.checkout_items is not None:
                for item in temp.checkout_items:
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

    def calculate_total(self, request, **kwargs):
        '''
        calculate total incl shipping
        note: 
        - if not on saved checkout:
        product calculations for VAT are not redone, rather, they are taken from the shopping cart viewset
        - else:
        product calculations are redone to match the product config price
        '''
        temp = kwargs.get('temp', None)
        if temp is not None:
            checkout_shipping_rate = kwargs.get('checkout_shipping_rate', 0)
            if temp.checkout_saved_instance:
                total_quantity = temp.checkout_items.count()
                subtotal_excl = 0
                if temp.checkout_instance == 'order':
                    for item in temp.checkout_items:
                        subtotal_excl += item.order_item_excl
            else:
                if temp.checkout_items is not None:
                    if temp.checkout_instance_type == 'order':
                        subtotal_excl = temp.shopping_cart_obj.subtotal
                        total_quantity = temp.shopping_cart_obj.total_quantity
                    if temp.checkout_instance_type == 'repair':
                        subtotal_excl = 0
                        total_quantity = 0
            shipping = checkout_shipping_rate
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
                super().set_temp(request, temp=temp)
                return Response(data, status=status.HTTP_200_OK)

    def initialize_user_addresses(self, request):
        fields = {'user_id': request.user.user_id}
        queryset = super().get_or_set(model='_user_addresses', extra_fields=fields, queryset=reg_models.UserAddresses.objects)
        serializer = UserAddressesSerializer(queryset, many=True)
        return serializer.data

    def initialize_user(self, request, **kwargs):
        '''
        initializes user details, from queryset or cache
        '''
        temp = kwargs.get('temp', None)
        if temp is not None:
            fields = {'user_id': request.user.user_id}
            queryset = super().get_or_set(model='_user_details', extra_fields=fields, queryset=reg_models.UserDetails.objects)
            temp.checkout_instance_user_details = queryset[0]

    def serialized_checkout_items(self, request, **kwargs):
        '''
        returns serialized versions of products
        '''
        temp = kwargs.get('temp', None)
        if temp is not None:
            if temp.checkout_instance_type == 'order':
                if temp.checkout_saved_instance:
                    super().retrieve_items(request, pk=temp.checkout_instance_id)
                else:
                    data = super().serialized_response(request, backend_req=True, exclude='shopping_cart', temp=temp)
                    # data = super().serialized_response(request, backend_req=True, temp=temp)
            if temp.checkout_instance_type == 'repair':
                serializer = st_model_serializers.ProductsSerializer(temp.checkout_items, context={'request': request}, many=True)
                data = serializer.data
            return data

    def check_active(self, **kwargs):
        temp = kwargs.get('temp', None)
        if temp is not None:
            if temp.checkout_instance_type == 'repair':
                items = [temp.checkout_items]
            else:
                items = temp.checkout_items
                temp.checked_ex_unit = False
                temp.contains_ex = False
            for item in items:
                if temp.checkout_instance_type == 'order':
                    if temp.checkout_saved_instance:
                        product_config_id = item.sku_no.product_config_id
                        product_id = product_config_id.product_id
                    else:
                        product_config_id = item.product_config_id
                        product_id = item.product_config_id.product_id
                    quantity = [i for i in items if i.product_config_id == product_config_id]
                    quantity = quantity.count(len(quantity))
                    if temp.checked_ex_unit == False:
                        if product_config_id.variation_id == 2:
                            temp.contains_ex = True
                            temp.checked_ex_unit = True
                    if (product_config_id.stock_available - 2) > quantity:
                        return Exception
                else:
                    product_id = item[0]
                if product_id.is_active == False:
                    return custom_exceptions.item_non_active_error('product')
            return True

    def run_checks(self, request, instance_type=None, pk=None, **kwargs):
        '''
        used for the retrieve() and payment_initialize_data() methods
        '''
        temp = kwargs.get('temp', None)
        self.initialize_user(request, temp=temp)
        if temp is not None:
            checkout_saved_instance = getattr(temp, 'checkout_saved_instance', False)
            temp.checkout_saved_instance = checkout_saved_instance
            if temp.checkout_saved_instance:
                if self.checkout_backend_load:
                    self.continue_saved_checkout(request, pk=pk, instance_type=instance_type, temp=temp)
            else:
                self.initialize_new(request, instance_type=instance_type, temp=temp)
            shipping_rate = self.get_shipping_method(request, temp=temp)
            checkout_total = self.calculate_total(request, temp=temp, checkout_shipping_rate=shipping_rate.get('checkout_shipping_rate', 0))
            data = {
                'checkout_total': checkout_total
            }
            self.check_active(temp=temp)
            if temp.checkout_instance_type == 'order':
                data['checkout_contains_ex'] = temp.contains_ex
            if self.checkout_on_load:
                data['checkout_items'] = self.serialized_checkout_items(request, temp=temp)
                data['user_addresses'] = self.initialize_user_addresses(request)
                data['active_address'] = getattr(temp, 'checkout_user_address', None)
            if self.checkout_backend_load:
                shipping_rate.pop('checkout_shipping_rate', '')
                data.append(**shipping_rate)
                if temp.checkout_instance_type == 'repair':
                    data['checkout_item_id'] = temp.checkout_items.pk
            super().set_temp(request, temp=temp)
            # temp2 = super().get_temp(request)
            print(temp.__dict__)
            return data

    def retrieve(self, request, instance_type=None, **kwargs):
        '''
        return initial values on page load
        '''
        self.checkout_on_load = True
        temp = kwargs.get('temp', super().get_temp(request))
        data = self.run_checks(request, instance_type=instance_type, temp=temp)
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
        temp = super().get_temp(request)
        data = self.run_checks(request, instance_type=instance_type, pk=pk, temp=temp)
        initial = {'initial': data}
        if temp.checkout_saved_instance:
            initial.append(**{f'{temp.checkout_instance_type}': temp.checkout_instance})
            action = 'update'
        else:
            action = 'create'
        instance = getattr(temp.checkout_instance_super, action)
        self.initialize_saved(instance(request, **initial))
        if temp.checkout_instance_type == 'order':
            if action == 'create':
                self.create_order_items(request, initial_data_items=temp.checkout_items, order_instance=temp.checkout_instance)
            if action == 'update':
                self.update_order_items(request, fields={'is_pending': True}, order_instance=temp.checkout_instance)
            if instance.contains_ex == True:
                update_or_delete_ex_images(request, order_instance=temp.checkout_instance)
        self.checkout_backend_load = False
        return super().initialize_form(request, temp=temp)

    @action(detail=True, methods=['get'], url_path=r'(?P<pk>\d+)')
    def continue_saved_checkout(self, request, pk=None, instance_type=None, **kwargs):
        if pk is not None:
            temp = kwargs.get('temp', None)
            if temp is None:
                temp = super().get_temp(request)
            temp.checkout_saved_instance = True
            self.initialize(instance_type=instance_type, temp=temp)
            self.initialize_saved(self.checkout_instance_model.objects.get(pk=pk), temp=temp)
            if instance_type == 'order':
                # child_model = getattr(temp.checkout_instance_super, 'child_model')
                get_private = getattr(temp.checkout_instance_super, 'get_private')
                child_model = get_private(['child_model'])
                prefetch_qs = getattr(temp.checkout_instance_super, 'def_prefetch_queryset')
                temp.checkout_items = child_model.objects.prefetch_related(prefetch_qs).filter(order_id=pk)
            if instance_type == 'repair':
                temp.checkout_items = temp.checkout_instance.product_id
                extra_vals = {'saved_reason_repair': temp.checkout_instance.reason_repair, 'saved_error_codes': temp.checkout_instance.error_codes}
            super().set_temp(request, temp=temp)
            return self.retrieve(request, instance_type=instance_type, extra_vals=extra_vals)

    @action(detail=False, methods=['get'], url_path=r'(?P<pk>\d+)/cancel')
    def payment_cancel(self, request, pk=None):
        '''
        if pk matches, sets instance (and items) to 'saved'
        '''
        temp = kwargs.get('temp', super().get_temp(request))
        if temp.checkout_instance_id == int(pk):
            current_status_id = {'current_status_id': 3,}
            fields = {
                **current_status_id,
                'current_status_date': date,
            }
            status_data = {
                **current_status_id,
                'subject': f'Your {temp.checkout_instance_type} {temp.checkout_instance_id} has been saved for future payment',
                'comment': '',
                'instance': self.checkout_instance,
                'comm_method': ''
            }
            update_status = getattr(temp.checkout_instance_super, 'update_status')
            update_status(request, **status_data)
            if temp.checkout_instance_type == 'order':
                self.update_order_items(request, pk=temp.checkout_instance_id, fields=fields)
            return Response({'message': f'successfully saved {temp.checkout_instance_type}'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'], url_path=r'(?P<pk>\d+)/recieve')
    def payment_recieve_data(self, request, pk=None):
        '''
        if pk matches, recieve data
        '''
        if temp.checkout_instance_id == int(pk):
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
        temp = super().get_temp()
        if temp.checkout_instance_id == pk:
            super().conduct_security_checks(request)
            if True:
                html_conf = getattr(temp.checkout_instance_super, 'render_conf')
                data = html_conf(request, instance=temp.checkout_instance, user_details=temp.checkout_instance_user_details)
                if temp.checkout_instance.shipping_method_id == 1:
                    super().create_shipment(request)
                    temp.checkout_instance.refresh_from_db()
                subject = f'Your {temp.checkout_instance_type} {temp.checkout_instance_id} is confirmed'
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
                send_conf = getattr(temp.checkout_instance_super, 'send_conf')
                update_status = getattr(temp.checkout_instance_super, 'update_status')
                if temp.checkout_instance_type == 'order':
                    status_data['current_status_id'] = 1
                if temp.checkout_instance_type == 'repair':
                    status_data['current_status_id'] = 2
                send_conf(request, **conf_data)
                update_status(request, **status_data)
                return Response(data, status=status.HTTP_201_CREATED)  
            else:
                return self.payment_cancel(request, pk=temp.checkout_instance_id, temp=temp)
                # return Response({'message': 'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid Checkout Instance ID'}, status=status.HTTP_400_BAD_REQUEST)

class ReturnsViewSet(custom_mixins.CommunicationViewSetMixin, custom_mixins.DefaultCacheMixin, viewsets.ViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]
    
    def_prefetch_queryset = Prefetch('order_item_id__sku_no__product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id'))

    __parent_serializer = auth_model_serializers.ReturnsSerializer
    __parent_serializer_ex = auth_serializers.ReturnsSerializerEx
    __parent_model = auth_models.Returns
    __parent_id_field = 'return_id'

    __history_serializer = auth_model_serializers.ReturnHistorySerializer
    __history_model = auth_models.ReturnHistory
    
    __comm_history_serializer = auth_model_serializers.ReturnCommunicationHistorySerializer
    __comm_history_model = auth_models.ReturnCommunicationHistory

    __obj_type = 'return'

    cache_list_fields = ['parent_model', 'user_id']
    cache_retrieve_fields = ['parent_model', 'parent_id_field']

    def get_private(self, attrs):
        return custom_utils.get_private(self=self, attrs=attrs)

    def list(self, request):
        queryset = super().list_cache(queryset=self.__parent_model.objects, user_id=request.user.user_id)
        serializer = self.__parent_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        return_serializer_dict = {}
        return_queryset = order_queryset = super().retrieve_cache(queryset=self.__parent_model.objects, return_id=pk)
        if return_queryset is not None:
            self.check_object_permissions(request, return_queryset)
            return_serializer = self.__parent_serializer(return_queryset)
            return_serializer_dict.update(**{'return_details': return_serializer.data})
        return_history_queryset = self.__history_model.objects.filter(return_id=pk)
        if return_history_queryset is not None:
            return_history_serializer = self.__history_serializer(return_history_queryset, many=True)
            return_serializer_dict.update(**{'return_history': return_history_serializer.data})
        if is_admin_req:
            return return_serializer_dict
        else:
            return Response(return_serializer_dict, status=status.HTTP_200_OK)

    def send_conf(self, request, **kwargs):
        return_instance = kwargs.get('return_instance', None)
        if return_instance is not None:
            return_serializer = self.__parent_serializer(return_instance)
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
        data = request.data
        data.update(**default)
        serializer = self.__parent_serializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            return_instance = serializer.save()
            request.session['return_instance'] = return_instance
            return_instance = __parent_model.objects.prefetch_related(self.def_prefetch_queryset).select_related('order_id').filter(pk=return_instance['repair_id']).first()
            super().list_cache(user_id=request.user.user_id, delete=True)
            return self.send_return_conf(request, return_instance=return_instance)