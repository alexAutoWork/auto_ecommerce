from rest_framework import viewsets, status, views, permissions
from . import auth_models, auth_model_serializers, auth_serializers, auth_utils
from . import auth_permissions, auth_mixins
from .. import serializers as custom_serializers, utils as custom_utils, mixins as custom_mixins
from ..reg.reg_model_serializers import UserAddressSerializer
from ..reg import reg_models
from ..standard import st_models
from ..external_api import external_api_views
import re, random, datetime, logging
from decimal import Decimal as dec

sage = external_api_views.SageAccountingIntegration
vat_perc = dec(0.15)
logger = logging.getLogger(__name__)

class ShoppingCartViewSet(viewsets.ModelViewSet):
    permission_classes = [auth_permissions.BaseAuthUserPermission]
    serializer_class = auth_model_serializers.ShoppingCartSerializer()

    def get_queryset(self, request):
        user = self.request.user
        shopping_cart_object = auth_models.ShoppingCart.objects.filter(user_id=user)
        serializer = self.serializer_class(data=shopping_cart_object)
        if shopping_cart_object.exists():
            request.session['shopping_cart_object'] = serializer.instance
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            self.create()

    def perform_create(self, serializer, request):
        user = self.request.user
        serializer.save(user_id=user)

    def perform_update(self, serializer, request, session):
        shopping_cart_object = request.session.get('shopping_cart_object')
        shopping_cart_id = shopping_cart_object['shopping_cart_id']
        shoppiing_cart_items = auth_models.ShoppingCartItems.objects.filter(shopping_cart_id=shopping_cart_id).values()
        shopping_cart_items_cal = []
        for items in shopping_cart_items:
            shopping_cart_item_quantity = dec(shopping_cart_items['quantity'])
            shopping_cart_item_total_price = dec(shopping_cart_items['total_price'])
            shopping_cart_item_total_price *= shopping_cart_item_quantity
            shopping_cart_items_cal.append(round(shopping_cart_item_total_price, 2))
        if 0:
            return 0
        else:
            for item in shopping_cart_items_cal:
                subtotal += item
                return dec(subtotal)
            vat = subtotal * vat_perc
            vat = round(vat, 2)
            total = subtotal + vat
            data = {
                'subtotal': subtotal,
                'vat': vat,
                'total': total
            }
            serializer.save(data=data)

class ShoppingCartItemsViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.BaseAuthUserPermission]
    serializer_class = auth_model_serializers.ShoppingCartItemsSerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['shopping_cart_id']
        field_parent_id  = 'shopping_cart_id'
        model_parent = auth_models.ShoppingCart()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['shopping_cart_id']
        field_parent_id = 'shopping_cart_id'
        model_parent = auth_models.ShoppingCartItems()
        model_serializer = auth_model_serializers.ShoppingCartItemsSerializer()

    def create(self, request):
        serializer = self.serializer_class(data=self.request.data)
        shopping_cart_object = request.session.get('shopping_cart_object')
        if serializer.is_valid(raise_exception=True):
            ShoppingCartViewSet.update(instance=shopping_cart_object, partial=True)
            return Response(status=status.HTTP_201_CREATED)

class Checkout(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['shopping_cart_id']
        field_parent_id  = 'shopping_cart_id'
        model_parent = auth_models.ShoppingCart()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['shopping_cart_id']
        field_parent_id = 'shopping_cart_id'
        model_parent = auth_models.ShoppingCartItems()
        model_serializer = auth_model_serializers.ShoppingCartItemsSerializer()

    def get_user_addresses(self, request):
        user = self.request.user
        user_address_objects = auth_models.UserAddresses.objects.filter(user_id=user)
        serializer = UserAddressSerializer(data=user_address_objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, format=None):
        self.get_parent_queryset()
        if True:
            queryset = self.get_child_queryset()
            serializer = auth_model_serializers.ShoppingCartItemsSerializer(data=queryset, many=True)
            request.session['get_shopping_cart_items'] = serializer.data
            return Response(serializer.data)

    def calculate_total_dim(self, request):
        shopping_cart_items = request.session.get('get_shopping_cart_items')
        shopping_cart_items_cal_dim_list = []
        for items in shopping_cart_items:
            product_config_id = item['product_config_id']
            quantity = dec(item['quantity'])
            products = st_models.ProductConfig.objects.filter(product_config_id=product_config_id).select_related('product_config_id__products_id').values('products_id', 'dimension_h', 'dimension_l', 'dimension_w', 'weight')
            products_id = products['products_id']
            dim_h = dec(products['dimension_h'])
            dim_l = dec(products['dimension_l'])
            dim_w = dec(products['dimension_w'])
            weight = dec(products['weight'])
            if quantity == 0:
                shopping_cart_items_cal_dim_dict = {
                    'product_id': product_id,
                    'dim_h': dim_h,
                    'dim_l': dim_l,
                    'dim_w': dim_w,
                    'weight': weight
                }
                shopping_cart_items_cal_dim_list.append(shopping_cart_items_cal_dim_dict)
            else:
                dim_h *= quantity
                dim_l *= quantity
                dim_w *= quantity
                weight *= quantity
                shopping_cart_items_cal_dim_dict = {
                    'product_id': product_id,
                    'dim_h': round(dim_h, 4),
                    'dim_l': round(dim_l, 4),
                    'dim_w': round(dim_w, 4),
                    'weight': round(weight, 4)
                }
                shopping_cart_items_cal_dim_list.append(shopping_cart_items_cal_dim_dict)
        if 0:
            return 0
        else:
            for item in shopping_cart_items_cal_dim_list:
                for key in item:
                    if key == 'dim_h':
                        total_dim_h += val
                    if key == 'dim_l':
                        total_dim_l += val
                    if key == 'dim_w':
                        total_dim_w += val
                    if key == 'weight':
                        total_weight += val
                data = {
                    'total_dim_h': round(total_dim_h, 4),
                    'total_dim_l': round(total_dim_l, 4),
                    'total_dim_w': round(total_dim_w, 4),
                    'total_weight': round(total_weight, 4)
                }
                return data
    
    def return_total_dim(self, request):
        serializer = auth_serializers.CheckoutTotalDimSerializer(data=self.calculate_total_dim())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def calculate_total(self, request):
        shopping_cart_items = request.session.get('get_shopping_cart_items')
        shopping_cart_items_cal_total_list = []
        for items in shopping_cart_items:
            total_price = dec(shopping_cart_items['total_price'])
            quantity = shopping_cart_items['quantity']
            shopping_cart_items_cal_total_dict = {
                'total_price': total_price,
                'quantity': quantity
            }
            shopping_cart_items_cal_total_list.append(shopping_cart_items_cal_total_dict)
        if 0:
            return 0
        else:
            for item in shopping_cart_items_cal_total_list:
                for key in item:
                    if key == 'total_price':
                        subtotal += val
                    if key == 'quantity':
                        total_quantity += val
                shopping_cart_items_total = [subtotal, total_quantity]
                return shopping_cart_items_total
            subtotal = dec(shopping_cart_items_total[0])
            total_quantity = shopping_cart_items_total[1]
            # shipping = shipping
            vat = subtotal * vat_perc
            vat = round(vat, 2)
            total = subtotal + vat
            data = {
                'total_quantity': total_quantity,
                # 'shipping': shipping,
                'subtotal': subtotal,
                'vat': vat,
                'total': total
            }
            return data
    
    def return_total(self, request):
        serializer = auth_serializers.CheckoutTotalSerializer(data=calculate_total())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def upload_exchange_unit_image(self, request):
        serializer = custom_serializers.JSONImageSerializer(data=request.data, many=True)
        if serializer.is_valid(raise_exception=True):
            json_images = image_url_to_json(serializer.validated_data)
            return Response(json_images)

    def contains_exchange_unit(self, request, session):
        shopping_cart_items = request.session.get('get_shopping_cart_items')
        if ('variation_id', '1') in shopping_cart_items.items():
            return True
        return False

    def post(self):
        OrdersViewSet.create()
        OrderItemsViewSet.create()
        if status.is_success():
            payfast = external_api_views.PayFastPayment()
            payfast.initialize_data()
            payfast.recieve_incoming_data()
            if status.is_success():
                self.notify()

    def notify(self, request, session):
        payfast = external_api_views.PayFastPayment()
        incoming_data = request.session.get('incoming_data')
        param_string = payfast.convert_incoming_data_to_params(incoming_data)
        payfast_check_1 = payfast.validate_signature(incoming_data, param_string)
        payfast_check_2 = payfast.validate_ip()
        payfast_check_3 = payfast.validate_payment_data(data=incoming_data)
        payfast_check_4 = payfast.validate_server_confirmation(param_string=param_string)

        if (payfast_check_1 and payfast_check_2 and payfast_check_3 and payfast_check_4):
            order_details_instance = request.session.get('order_details_instance')
            order_id = order_details_instance['order_id']
            comm_object_data = {
                'serializer': auth_model_serializers.OrdersSerializer,
                'serializer_add': auth_model_serializers.OrderItemsSerializer,
                'serializer_comm_history': auth_model_serializers.OrderCommunicationHistorySerializer,
                'user_id': request.user.user_id,
                'obj_type': 'order',
                'type_id': order_id,
                'comm_type': 'conf',
                'subject': f'Order {order_id} confirmed!',
                'comment': f'Thank you, Order {order_id} has been placed! We\'ll you know as soon as we\'ve recieved payment'
            }
            comm_object = custom_mixins.SendEmailConfViewSetMixin(**comm_object_data)
            order_details_instance = request.session.get('order_details_instance')
            comm_object.render_conf(sr_data=order_details_instance)
            InvoiceViewSet.create()
            return Response(status=status.HTTP_200_OK)
        else:
            logger.debug(payfast_check_1, payfast_check_2, payfast_check_3, payfast_check_4)

class OrdersViewSet(viewsets.ModelViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]
    serializer_class = auth_model_serializers.OrdersSerializer()

    def get_queryset(self, request):
        user = self.request.user
        serializer = self.serializer_class()
        queryset = auth_models.Orders.objects.filter(user_id=user)
        return serializer(data=queryset, many=True)

    def perform_create(self, serializer, request, session):
        dim = Checkout.calculate_total_dim()
        total = Checkout.calculate_total()
        data = {
            'user_id': self.request.user,
            'order_date': datetime.date.today(),
            'order_subtotal': total['subtotal'],
            'order_tax': total['vat'],
            'order_total': total['total'],
            'order_total_dim_h': dim['total_dim_h'],
            'order_total_dim_l': dim['total_dim_l'],
            'order_total_dim_w': dim['total_dim_w'],
            'order_total_dim_weight': dim['total_weight'],
            'contains_exchange_unit': Checkout.contains_exchange_unit(),
            'exchange_unit_img': Checkout.upload_exchange_unit_image(),
            'is_cancelled': False,
            'is_completed': False,
            'current_status_id': 1,
            'current_status_date': datetime.date.today()
        }
        serializer.save(data=data)

    def create(self, request):
        serializer = self.serializer_class()
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            request.session['order_details_instance'] = serializer.instance
            return Response(status=status.HTTP_201_CREATED)

    def update_status_on_successful_payment(self, request):
        order_details_instance = request.session.get('order_details_instance')
        order_id = order_details_instance['order_id']
        user_id = order_details_instance['user_id']
        comm_object_data = {
            'serializer': self.serializer_class,
            'serializer_add': auth_model_serializers.OrderHistorySerializer,
            'serializer_comm_history': auth_model_serializers.OrderCommunicationHistorySerializer,
            'instance': order_details_instance,
            'user_id': user_id,
            'obj_type': 'order',
            'type_id': order_id,
            'comm_type': 'status',
            'subject': f'Order {order_id} paid',
            'comment': f'Success! Your Order {order_id} has been successfully paid and is now ready to be processed.'
        }
        comm_object = custom_mixins.UpdateStatusViewSetMixin(**comm_object_data)
        return comm_object.update_status(current_status_id='2', comm_method='SMS, email')

class OrderItemsViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]
    serializer_class = auth_model_serializers.OrderItemsSerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['order_id']
        field_parent_id  = 'order_id'
        model_parent = auth_models.Orders()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['order_id']
        field_parent_id = 'order_id'
        model_parent = auth_models.OrderItems()
        model_serializer = auth_model_serializers.OrderItemsSerializer()

    def perform_create(self, serializer, **kwargs):
        data = {
            'order_id': kwargs.get('order_id'),
            'sku_no': self.return_random_stock(kwargs.get('product_config_id')),
            'order_item_price': kwargs.get('order_item_price')
        }
        serializer.save(data=data)

    def create(self, request, session):
        items = request.session.get('get_shopping_cart_items')
        quantity = items['quantity']
        order_item_price = float(items['order_item_price']) / float(quantity)
        order_details_instance = request.session.get('order_details_instance')
        data = {
            'product_config_id': items['product_config_id'],
            'order_id': order_details_instance['order_id'],
            'order_item_price': order_item_price
        }
        serializer = self.serializer_class(many=True)
        i = 0
        order_item_instances = []
        while i > int(quantity):
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer, **data)
                order_item_instances.append(serializer.instance)
        request.session['order_item_instances'] = order_item_instances
        return Response(status=status.HTTP_201_CREATED)

    def return_random_stock(self, product_config_id):
        product_stock = ProductStock.objects.filter(product_config_id=product_config_id, is_purchased=False).values_list('sku_no', flat=True)
        return random.choice(product_stock)

class OrderHistoryViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.SystemObjectAuthUserPermission]
    serializer_class = auth_model_serializers.OrderHistorySerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['order_id']
        field_parent_id  = 'order_id'
        model_parent = auth_models.Orders()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['order_id']
        field_parent_id = 'order_id'
        model_parent = auth_models.OrderHistory()
        model_serializer = auth_model_serializers.OrderHistorySerializer()

class OrderCommunicationHistoryViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.SystemObjectAuthUserPermission]
    serializer_class = auth_model_serializers.OrderCommunicationHistorySerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['order_id']
        field_parent_id  = 'order_id'
        model_parent = auth_models.Orders()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['order_id']
        field_parent_id = 'order_id'
        model_parent = auth_models.OrderCommunicationHistory()
        model_serializer = auth_model_serializers.OrderCommunicationHistorySerializer()

class InvoiceViewSet(custom_mixins.CommunicationViewSetObjectMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]
    serializer_class = auth_model_serializers.InvoicesSerializer()

    def get_queryset(self, request):
        user = self.request.user
        serializer = self.serializer_class()
        queryset = auth_models.Invoices.objects.filter(user_id=user)
        return serializer(data=queryset)

    def comm_object(self, **kwargs):
        super(custom_mixins.CommunicationViewSetObjectMixin, self).__init__(**kwargs)
    
    def perform_create(self, serializer, request, session):
        order_details_instance = request.session.get('order_details_instance')
        order_id = order_details_instance['order_id']
        user = self.request.user
        data = {
            'user_id': user,
            'order_id': order_id,
            'is_synced': False
        }
        serializer.save(data=data)

    def create(self, request):
        serializer = self.serializer_class()
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            request.session['invoice_details_instance'] = serializer.instance
            InvoiceItemsViewSet.create()
            self.create_pdf()
            self.send_pdf()
            self.sync_to_sage()
            return Response(status=status.HTTP_201_CREATED)

    def create_pdf(self, request):
        self.render_invoice()
        pdf_filename = request.session.get('pdf_filename')
        pdf_file = self.return_invoice_path(pdf_filename)
        invoice_details_instance = request.session.get('invoice_details_instance')
        serializer = self.serializer_class(instance=invoice_details_instance, data={'download_link': pdf_file}, partial=True)

    def send_pdf(self, request):
        invoice_details_instance = request.session.get('invoice_details_instance')
        invoice_id = invoice_details_instance['invoice_id']
        comm_object_data = {
            'serializer_comm_history': auth_model_serializers.OrderCommunicationHistorySerializer,
            'user_id': invoice_details_instance['user_id'],
            'obj_type': 'invoice',
            'type_id': invoice_id,
            'comm_type': 'pdf-attachment',
            'subject': f'Invoice {invoice_id} attached',
            'comment': f'Please find your invoice attached'
        }
        comm_object = self.comm_object(**comm_object_data)
        pdf_filename = request.session.get('pdf_filename')
        pdf_file = self.return_invoice_path(pdf_filename)
        self.send_email(comm_object, data=None, data_add=None, attachment=pdf_file)

    def save_to_comm_history(self, comm_object, comm_method, comm_recipient):
        invoice_details_instance = request.session.get('invoice_details_instance')
        order_id = invoice_details_instance['order_id']
        data = {
            'user_id': comm_object.user_id,
            'order_id': order_id,
            'comm_method': comm_method,
            'comm_type': comm_object.comm_type,
            'comm_recipient': comm_recipient,
            'comm_date': comm_object.date,
            'comm_subject': comm_object.subject,
            'comm_comment': comm_object.comment
        }
        serializer = comm_object.serializer_comm_history(data=data)
        serializer.save()

    def render_invoice(self, request):
        invoice_details_instance = request.session.get('invoice_details_instance')
        order_details_instance = request.session.get('order_details_instance')
        order_item_instances = request.session.get('order_item_instances')
        order_item_instance_objects = order_item_instances.select_related('sku_no__product_config_id__variation_id').values('products_id', 'name', 'value', 'order_item_price')
        user_id = invoice_details_instance['user_id']
        user_details = reg_models.UserDetails.objects.filter(user_id=user_id).select_related('user_id').values('email', 'mobile_no', 'name', 'surname', 'company', 'company_reg_no', 'vat_no', 'sage_id')
        user_details_name = user_details['name']
        user_details_surname = user_details['surname']
        user_details_name = f'{user_details_name} {user_details_surname}'
        request.session['pdf_filename'] = pdf_filename
        data_add = []
        for item in order_item_instance_objects:
            excl = dec(item['order_item_price'])
            vat = excl * vat_perc
            vat = round(vat, 2)
            incl = excl + vat
            invoice_items_dict = {
                'invoice_item_code': item['products_id'],
                'invoice_item_sku_no': item['sku_no'],
                'invoice_item_name': item['name'],
                'invoice_item_variation': item['value'],
                'invoice_item_excl': excl,
                'invoice_item_vat': vat,
                'invoice_item_incl': incl
            }
            data_add.append(invoice_items_dict)
        data = {
            'filename': filename,
            'invoice_id': invoice_details_instance['invoice_id'],
            'order_id': order_details_instance['order_id'],
            'invoice_date': order_details_instance['order_date'],
            'customer_name': user_details_name,
            'customer_email': user_details['email'],
            'customer_mobile': user_details['mobile_no'],
            'customer_company': user_details['company'],
            'customer_reg_no': user_details['company_reg_no'],
            'customer_vat_no': user_details['vat_no'],
            'invoice_shipping': order_details_instance['shipping_price'],
            'invoice_excl': order_details_instance['order_subtotal'],
            'invoice_vat': order_details_instance['order_tax'],
            'invoice_total': order_details_instance['order_total'],
            'invoice_items': data_add
        }
        serializer = auth_serializers.InvoiceRenderSerializer(data=data)
        del request.session['order_details_instance']
        del request.session['order_item_instances']
        return Response(serializer_data.data, status=status.HTTP_200_OK)

    def return_invoice_path(self, filename):
        pdf_file = os.path.join(settings.MEDIA_ROOT, f'{filename}')
        if os.path.isfile(pdf_file):
            return pdf_file

    def sync_to_sage(self):
        invoice_details_instance = request.session.get('invoice_details_instance')
        invoice_id = invoice_details_instance['invoice_id']
        user_id = invoice_details_instance['user_id']
        sage.get_customer(user_id=user_id)
        sage.get_invoice(invoice_id=invoice_id)
        del request.session['invoice_details_instance']

class InvoiceItemsViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]
    serializer_class = auth_model_serializers.InvoiceItemsSerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['invoice_id']
        field_parent_id  = 'invoice_id'
        model_parent = auth_models.Invoices()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['invoice_id']
        field_parent_id = 'invoice_id'
        model_parent = auth_models.InvoiceItems()
        model_serializer = auth_model_serializers.InvoiceItemsSerializer()

    def perform_create(self, serializer, invoice_id, order_item_id):
        data = {
            'invoice_id': invoice_id,
            'order_item_id': order_item_id
        }
        serializer.save(data=data)

    def create(self, request, session):
        order_details_instance = request.session.get('order_details_instance')
        order_id = order_details_instance['order_id']
        invoice_details_instance = request.session.get('invoice_details_instance')
        invoice_id = invoice_details_instance['invoice_id']
        order_item_instances = request.session.get('order_item_instances')
        serializer = self.serializer_class()
        for item in order_item_instances:
            order_item_id = item['order_item_id']
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer, invoice_id, order_item_id)
        return Response(status=status.HTTP_201_CREATED)

class ReturnsViewSet(viewsets.ModelViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]
    serializer_class = auth_model_serializers.ReturnsSerializer()

    def get_queryset(self, request):
        user = self.request.user
        return auth_models.Returns.objects.filter(user_id=user)

class ReturnHistoryViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.SystemObjectAuthUserPermission]
    serializer_class = auth_model_serializers.ReturnHistorySerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['return_id']
        field_parent_id  = 'return_id'
        model_parent = auth_models.Returns()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['return_id']
        field_parent_id = 'return_id'
        model_parent = auth_models.ReturnHistory()
        model_serializer = auth_model_serializers.ReturnHistorySerializer()

class ReturnCommunicationHistoryViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.SystemObjectAuthUserPermission]
    serializer_class = auth_model_serializers.ReturnCommunicationHistorySerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['return_id']
        field_parent_id  = 'return_id'
        model_parent = auth_models.Returns()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['return_id']
        field_parent_id = 'return_id'
        model_parent = auth_models.ReturnCommunicationHistory()
        model_serializer = auth_model_serializers.ReturnCommunicationHistorySerializer()

class RepairsViewSet(viewsets.ModelViewSet):
    permission_classes = [auth_permissions.ObjectAuthUserPermission]
    serializer_class = auth_model_serializers.RepairsSerializer()

    def get_queryset(self, request):
        user = self.request.user
        return auth_models.Repairs.objects.filter(user_id=user)

class RepairHistoryViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.SystemObjectAuthUserPermission]
    serializer_class = auth_model_serializers.RepairHistorySerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['repair_id']
        field_parent_id  = 'repair_id'
        model_parent = auth_models.Repairs()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['repair_id']
        field_parent_id = 'repair_id'
        model_parent = auth_models.RepairHistory()
        model_serializer = auth_model_serializers.RepairHistorySerializer()

class RepairCommunicationHistoryViewSet(auth_mixins.ChildObjectAuthUserViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [auth_permissions.SystemObjectAuthUserPermission]
    serializer_class = auth_model_serializers.RepairCommunicationHistorySerializer()

    def get_parent_queryset(self, request):
        model_parent_id = self.request.data['repair_id']
        field_parent_id  = 'repair_id'
        model_parent = auth_models.Repairs()

    def get_child_queryset(self, request):
        model_parent_id = self.request.data['repair_id']
        field_parent_id = 'repair_id'
        model_parent = auth_models.RepairCommunicationHistory()
        model_serializer = auth_model_serializers.RepairCommunicationHistorySerializer()