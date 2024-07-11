from rest_framework import viewsets, status, views, permissions
from rest_framework.decorators import action
from django.conf import settings
from . import external_api_serializers
import hashlib, urllib.parse, base64, requests
from socket import gethostbyname_ex
from ..reg import reg_models, reg_model_serializers
from ..auth.auth_models import Invoices, InvoiceItems
from ..auth.auth_model_serializers import InvoicesSerializer, InvoiceItemsSerializer
from ..standard import st_models, st_model_serializers
from .. import utils, exceptions
from django.db.models import Prefetch
from celery import shared_task
import json

payfast_exc = exceptions.ServerPayFastError

class PayfastIntegration(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    # ex_api_instance_type = None
    # ex_api_instance_model = None
    # ex_api_instance_serializer = None
    # ex_api_instance_id_field = None
    # ex_api_instance_id = None
    # ex_api_instance = None
    # ex_api_user_details_instance = None

    def generate_signature(self, data_array, pass_phrase = ''):
        payload = ''
        for key in data_array:
            payload += key + '=' + urllib.parse.quote_plus(data_array[key].replace('+', ' ')) + '&'
        payload = payload[:-1]
        if pass_phrase != '':
            payload += f'&passphrase={pass_phrase}'
        return hashlib.md5(payload.encode()).hexdigest()

    def initialize_form(self, request, **kwargs):
        '''
        initialize html form for payment on frontend
        SEE BELOW FOR NOTES vvvv

        !!!note!!!
        while PayFast does have integration for API available,
        this requires storage of sensitive credit card information on our services,
        of which we DO NOT have the security to facilitate
        and yes, while this does violate some REST API principles, I'd rather that than risk someone's credit card information being exposed
        ~ sincerely, the original backend dev
        '''
        temp = kwargs.get('temp', None)
        if temp is not None:
            user = request.user
            user_details = temp.checkout_instance_user_details
            if temp.checkout_instance_type == 'repair':
                amount = temp.checkout_instance.shipping_price_incl
            if temp.checkout_instance_type == 'order':
                amount = temp.checkout_instance.order_total
            else:
                raise exceptions.invalid_error('checkout type')
            data = {
                'merchant_id': settings.PAYFAST_ID,
                'merchant_key': settings.PAYFAST_KEY,
                'return_url': f'http://localhost:8080/conf/{temp.checkout_instance_type}/{temp.checkout_instance_id}/',
                'cancel_url': f'http://localhost:8080/cancel/{temp.checkout_instance_type}/{temp.checkout_instance_id}/',
                'notify_url': f'http://localhost:3000/auth/checkout/{temp.checkout_instance_id}/recieve',
                'name_first': user_details.name,
                'name_last': user_details.surname,
                'email_address': user.email,
                'cell_number': user.mobile_no,
                'amount': amount,
                'item_name': temp.checkout_instance_id
            }
            pass_phrase = settings.PAYFAST_PASS_PHRASE
            data['security_signature'] = self.generate_signature(data, pass_phrase)
            request.session['initialized_data'] = data
            serializer = external_api_serializers.PayFastSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data, status=status.HTTP_200_OK)

    def recieve_data(self, request):
        data = request.data
        request.session['recieve_data'] = data
        return Response(status=status.HTTP_200_OK)

    def convert_incoming_data_to_params(self, data):
        param_string = ''
        for [key] in data:
            if [key] != 'signature':
                param_string += [key] + '=' + urllib.parse.quote_plus(data[key].replace('+', ' ')) + '&'
        param_string = param_string[:-1]
        return param_string
    
    def validate_signature(self, data, param_string):
        signature = hashlib.md5(param_string.encode()).hexdigest()
        if data.get('signature') != signature:
            raise payfast_exc.failure('signature')
            # raise exceptions.payfast_invalid_error('signature')

    def validate_ip(self):
        valid_hosts = [
            'www.payfast.co.za',
            'sandbox.payfast.co.za',
            'w1w.payfast.co.za',
            'w2w.payfast.co.za'
        ]
        valid_ips = []
        for item in valid_hosts:
            ips = gethostbyname_ex(item)
            if ips:
                for ip in ips:
                    if ip:
                        valid_ips.append(ip)
        clean_valid_ips = []
        for item in valid_ips:
            if isinstance(item, list):
                for prop in item:
                    if prop not in clean_valid_ips:
                        clean_valid_ips.append(prop)
            else:
                if item not in clean_valid_ips:
                    clean_valid_ips.append(item)
        
        if urllib.parse.urlparse(request.headers.get('Referrer')).hostname not in clean_valid_ips:
            raise exceptions.payfast_invalid_error('IP')

    def validate_payment_data(self, rec_data, ini_data):
        amount = ini_data['amount']
        amount_gross = rec_data.get('amount_gross')
        if not (abs(amount) - amount_gross) > 0.01:
            raise exceptions.payfast_invalid_error('gross amount')

    def validate_server_confirmation(self, param_string, host = 'sandbox.payfast.co.za'):
        url = f'https://{host}/eng/query/validate'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, data=param_string, headers=headers)
        if response.text != 'VALID':
            raise exceptions.payfast_invalid_error('server response')

    def conduct_security_checks(self, request):
        rec_data = request.session['recieve_data']
        ini_data = request.session['initialized_data']
        param_string = self.convert_incoming_data_to_params(rec_data)
        self.validate_signature(rec_data, param_string)
        self.validate_ip()
        self.validate_payment_data(rec_data, ini_data)
        self.validate_server_confirmation(param_string)
        return True

class SageAccountingIntegration(views.APIView):
    base_url = f'{settings.SAGE_URL}/api/{settings.SAGE_VER}'

    def encode_to_base64(self, input_val):
        input_val = input_val.encode('ascii')
        base64_val = base64.b64encode(input_val)
        base64_val = base64_val.decode('ascii')
        return base64_val

    def authorization(self):
        username = self.encode_to_base64(settings.SAGE_USERNAME)
        password = self.encode_to_base64(settings.SAGE_PASSWORD)
        encoded_credentials = username + ':' + password

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Basic {encoded_credentials}'
        }
        return headers

    def send_request(self, data, service_name, method_name, **params):
        headers = self.authorization()
        url = f'{base_url}/{service_name}/{method_name}/{str(**params)}'
        if method_name == 'Save':
            return requests.post(url=url, data=data, headers=headers)
        if method_name == 'Get':
            return requests.get(url=url, headers=headers)

    def get_customer(self, user_id, **kwargs):
        user_obj = reg_models.UserDetails.objects.select_related('user_id').filter(user_id=user_id)
        user_sage_id = user_obj.sage_id
        if user_sage_id is not None:
            params = f'{user_sage_id}'
            get_customer_request = self.send_request(data=None, service_name='Customer', method_name='Get', **params)
            if get_customer_request.status_code != '200' or '202':
                return self.save_customer(user_id=user_id)
            else:
                return user_sage_id
        else:
            return self.save_customer(user_obj=user_obj)

    def save_customer(self, **kwargs):
        user_obj = kwargs.get('user_obj', None)
        if user_obj is not None:
            if user_obj.user_id.is_verified == True:
                # contact_name = user_details_object['name'] + user_details_object['surname']
                contact_name = f'{user_obj.name} {user_obj.surname}'
                if user_obj.company is None:
                    company_name = contact_name
                else:
                    company_name = user_id.company
                data = {
                    'Name': company_name,
                    'TaxReference': user_obj.vat_no,
                    'Mobile': user_obj.user_id.mobile_no,
                    'Email': user_obj.user_id.email,
                    'ContactName': contact_name
                }
                serializer = external_api_serializers.SageCustomerSerializer(data=data)
                params = 'Save'
                save_customer_request = self.send_request(data=serializer.data, service_name='Customer', method_name=params, **params)
                if save_customer_request.status_code == '201':
                    save_customer_request_data = save_customer_request.json()
                    sage_id = save_customer_request_data['ID']
                    user_id.sage_id = sage_id
                    user_id.is_synced = True
                    user_id.save()
                    return sage_id
                    # return user_details_object.update(sage_id=sage_id, is_synced=True)

    def get_item(self, sku_no):
        # item_details = st_models.ProductConfig.objects.filter(products_id=products_id).values('sage_id')
        sku_obj = st_models.ProductStock.objects.select_related('product_config_id__product_id', 'product_config_id__variation_id').filter(sku_no=sku_no)
        if sku_obj.product_config_id.sage_id is not None:
            params = f'{item_details}'
            get_item_request = self.send_request(data=None, service_name='Item', method_name='Get', **params)
            if get_item_request.status_code != '200' or '202':
                return self.save_item(products_id=products_id)
            else:
                return sku_obj.sage_id

    def save_item(self, sku_obj):
        name = sku_obj.product_config_id.product_id.name
        variation = sku_obj.product_config_id.variation_id.variation_value
        description = f'{name} {variation}'
        data = {
            # 'Code': item_details_values['sage_item_code'],
            'Code': sku_obj.product_config_id.sage_item_code,
            'Description': description,
            'PriceExclusive': sku_obj.product_config_id.price
        }
        serializer = external_api_serializers.SageItemSerializer(data=data)
        save_item_request = self.send_request(data=serializer.data, service_name='Item', method_name='Save')
        if save_item_request.status_code == '201':
            save_item_request_data = save_item_request.json()
            sage_id = save_item_request_data['ID']
            sku_obj.product_config_id.sage_id = sage_id
            sku_obj.save()
            return sage_id

    def get_invoice(self, invoice_id):
        if invoice_id.sage_id is not None:
            params = f'{invoice_id.sage_id}'
            get_invoice_request = self.send_request(data=None, service_name='TaxInvoice', method_name='Get', **params)
            if get_invoice_request.status_code != '200' or '202':
                return self.save_invoice(invoice_id=invoice_id)
            else:
                return True

    def save_invoice(self, invoice_obj, customer_id):
        invoice_id = invoice_obj.pk
        invoice_items_prefetch_queryset = Prefetch('order_item_id__sku_no__product_config_id', queryset=st_models.ProductConfig.objects.select_related('product_id', 'variation_id'))
        invoice_items = InvoiceItems.objects.prefetch_related(invoice_items_prefetch_queryset).filter(invoice_id=invoice_id)
        invoice_items_list = []
        for item in invoice_items:
            sku_details = item.order_item_id.sku_no
            product_config_details = sku_details.product_config_id
            sage_item_id = product_config_details.sage_id
            sage_item_id = self.get_item(sku_no=sku_details.pk)
            invoice_items_dict = {
                'SelectionId': product_config_details.sage_item_code,
                'Description': sku_details.pk,
                'Exclusive': item.order_item_id.order_item_excl,
                'Quantity': 1
            }
            invoice_items_list.append(invoice_items_dict)
        order_details = invoice_obj.order_id
        data = {
            'CustomerId': customer_id,
            'Date': order_details.order_date,
            'Reference': f'{order_details.pk} [{invoice_id}]',
            'Exclusive': order_details.order_subtotal_excl,
            'Tax': order_details.order_tax,
            'Total': order_details.order_total,
            'Lines': invoice_items_list
        }
        serializer = external_api_serializers.SageInvoiceSerializer(data=data)
        save_invoice_request = self.send_request(data=serializer.data, service_name='TaxInvoice', method_name='Save')
        if save_invoice_request.status_code == '201':
            save_invoice_request_data = save_invoice_request.json()
            sage_id = save_invoice_request_data['ID']
            sage_doc_no = save_invoice_request_data['DocumentNumber']
            invoice_obj.update(is_synced=True, sage_id=sage_id, sage_doc_no=sage_doc_no)
            return sage_id

    def bulk_invoice_sync(self):
        invoices = Invoices.objects.prefetch_related('invoice_id__order_id').filter(is_synced=False)
        for invoice in invoices:
            customer = self.get_customer(user_id=invoice.user_id)
            self.save_invoice(invoice, customer)

class BobGoIntegration(viewsets.ViewSet):
    ex_api_bobgo_parcels = None

    def configure_user_address(self, **kwargs):
        '''
        configure user address to BobGo API Format
        '''
        temp = kwargs.get('temp', None)
        if temp is not None:
            user_address_obj = temp.checkout_user_address
            if user_address_obj.unit_number != None or 'null':
                street_address = f'{user_address_obj.unit_number} {user_address_obj.address_line_1}'
            else:
                street_address = f'{user_address_obj.address_line_1}'
            user_address_data = {
                'name': user_address_obj.name,
                'mobile_no': user_address_obj.contact_number,
                'street_address': street_address,
                'local_area': user_address_obj.area,
                'city': user_address_obj.city,
                'zone': user_address_obj.province,
                'code': user_address_obj.postal_code
            }
            if user_address_obj.company != None or 'null':
                user_address_data['company'] = user_address_obj.company
            if user_address_obj.email_address != None or 'null':
                user_address_data['email'] = user_address_obj.email_address
            return user_address_data

    def address_order(self, user_address_data, **kwargs):
        '''
        configure address order of user address + autolectronix address, based on if the checkout type is repair or order
        '''
        is_shipment = kwargs.get('is_shipment', False)
        temp = kwargs.get('temp', None)
        if temp is not None:
            if temp.checkout_instance_type == 'repair':
                collection_address = user_address_data
                delivery_address = settings.BOBGO_DEFAULT_COLLECTION_ADDRESS
            else:
                collection_address = settings.BOBGO_DEFAULT_COLLECTION_ADDRESS
                delivery_address = user_address_data
            addresses = [collection_address, delivery_address]
            contact_vals = ['name', 'mobile_no', 'email', 'company']
            if is_shipment == False:
                for item in contact_vals:
                    for address in addresses:
                        try:
                            del address[item]
                        except KeyError:
                            continue
            return addresses

    def initialize_parcels(self, **kwargs):
        '''
        interate through checkout items -> append with necessary data based on quantity
        '''
        temp = kwargs.get('temp', None)
        if temp is not None:
            checkout_items = temp.checkout_items
            # checkout_items = json.dumps(list(checkout_items))
            items = {}
            is_shipment = kwargs.get('is_shipment', False)
            for item in checkout_items:
                if temp.checkout_instance_type == 'order':
                    quantity = item.quantity
                    product_id = item.product_config_id.product_id
                if temp.checkout_instance_type == 'repair':
                    quantity = 1
                    product_id = item
                # quantity = item['quantity']
                # product_id = product_id.pk
                weight = product_id.weight
                weight_type = getattr(product_id, 'weight_type', None)
                # weight_type = product_id.weight_type
                if weight_type is not None:
                    if weight_type.lower() != 'kg':
                        weight = weight / 1000
                for i in range(quantity):
                    data = {
                        'description': '',
                        'submitted_length_cm': round(product_id.dimension_l),
                        'submitted_width_cm': round(product_id.dimension_w),
                        'submitted_height_cm': round(product_id.dimension_h),
                        'submitted_weight_kg': round(weight),
                        # 'custom_parcel_reference': ''
                    }
                    # data = {
                    #     'submitted_length_cm': 2.00,
                    #     'submitted_width_cm': 2.00,
                    #     'submitted_height_cm': 2.00,
                    #     'submitted_weight_kg': 2.00
                    # }
                    items.update(**data)
            print(items)
            return items

    def get_courier_rates_for_products(self):
        '''
        function to auto populate shipping rate data of individual products, scheduled on weekly basis
        '''
        url = f'${settings.BOBGO_URL}/rates'
        products = st_models.Products.objects.all()
        cities = st_models.Cities.objects.all()
        base_shipping_rate_data = []
        for product in products:
            if product.weight_type != 'kg' or 'KG' or 'Kg':
                product_weight = product.weight / 1000
            else:
                product_weight = product.weight
            for city in cities:
              data = {
                'collection_address': settings.BOBGO_DEFAULT_COLLECTION_ADDRESS,
                'delivery_address': {
                    'street_address': city.ram_address_1,
                    'local_area': city.local_area,
                    'city': city.city_value,
                    'zone': city.region_code,
                    'code': city.postal_code
                },
                'parcels': [
                    {
                        'description': '',
                        'submitted_length_cm': product.dimension_l,
                        'submitted_width_cm': product.dimension_w,
                        'submitted_height_cm': product.dimension_h,
                        'submitted_weight_kg': product_weight,
                        'custom_parcel_reference': ''
                    }
                ],
                'declared_value': 0,
                'timeout': 10000,
                'providers': ['RAM'],
                'service_levels': ['ECO']
              }
              print(data)
              serializer = external_api_serializers.BobGoCourierRateSerializer(data=data)
              if serializer.is_valid(raise_exception=True):
                courier_rate_request = requests.post(url=url, data=serializer.data, headers=settings.BOBGO_DEFAULT_HEADERS)
                if courier_rate_request.status_code == '201':
                    courier_rate_request_data = courier_rate_request.json()
                    if courier_rate_request_data['provider_rate_requests'][0]['status'] == 'success':
                        data2 = {
                            'city_id': city.city_id,
                            'product_id': product.product_id,
                            'base_charge': courier_rate_request_data['provider_rate_requests'][0]['responses'][0]['rate_amount'],
                        }
                        base_shipping_rate_data.append(data2)
                    else:
                        break
                else:
                    break
        serializer2 = st_model_serializers.BaseShippingRatesSerializer(data=base_shipping_rate_data, many=True)
        if serializer2.is_valid(raise_exception=True):
            st_models.BaseShippingRates.objects.all().delete()
            return serializer2.save()
    
    def get_checkout_rate(self, request, **kwargs):
        '''
        get rate of shipping at checkout (order/repair)
        '''
        temp = kwargs.get('temp', None)
        if temp is not None:
            url = f'{settings.BOBGO_URL}/rates'
            user_address_data = self.configure_user_address(temp=temp)
            print(user_address_data)
            address = self.address_order(user_address_data, temp=temp)
            parcels = self.initialize_parcels(temp=temp)
            temp.ex_api_bobgo_parcels = parcels
            data = {
                'collection_address': address[0],
                'delivery_address': address[1],
                'parcels': [
                    parcels
                ],
                'timeout': 10000,
                'providers': ['demo'],
                'service_levels': ['ECO']
            }
            print(data)
            data = json.dumps(data)
            print(data)
            courier_rate_request = requests.post(url=url, data=data, headers=settings.BOBGO_DEFAULT_HEADERS)
            print(courier_rate_request.status_code)
            print(courier_rate_request.text)
            if courier_rate_request.status_code == '201' or '200':
                courier_rate_request_data = courier_rate_request.json()
                if courier_rate_request_data['provider_rate_requests'][0]['status'] == 'success':
                    data2 = courier_rate_request_data['provider_rate_requests'][0]['responses'][0]['rate_amount_excl_vat']
                    return data2
            # serializer = external_api_serializers.BobGoCourierRateSerializer(data=data)
            # if serializer.is_valid(raise_exception=True):
            #     print(serializer.data)
            #     print(settings.BOBGO_DEFAULT_HEADERS)
            #     courier_rate_request = requests.post(url=url, data=serializer.data, headers=settings.BOBGO_DEFAULT_HEADERS)
            #     print(courier_rate_request.status_code)
            #     print(courier_rate_request.text)
            #     if courier_rate_request.status_code == '201' | '200':
            #         courier_rate_request_data = courier_rate_request.json()
            #         if courier_rate_request_data['provider_rate_requests'][0]['status'] == 'success':
            #             data2 = {
            #                 'shipping_price': courier_rate_request_data['provider_rate_requests'][0]['responses'][0]['rate_amount_excl_vat']
            #             }
            #             return data

    def create_shipment(self, request, **kwargs):
        '''
        create shipment at checkout (order/repair) after successful payment
        '''
        temp = kwargs.get('temp', None)
        if temp is not None:
            url = f'${settings.BOBGO_URL}/shipments'
            parcels = temp.ex_api_bobgo_parcels
            if temp.checkout_instance is not None:
                if self.checkout_user_address is not None:
                    user_address_data = self.configure_user_address()
                    address = self.address_order(user_address_data, is_shipment=True)
                    addresses = {'collection_address': address[0], 'delivery_address': address[1]}
                    for parcel in parcels:
                        parcel.pop('description', '')
                        parcel.pop('custom_parcel_reference', '')
                    address_vals = ['name', 'mobile_no', 'email', 'company']
                    address_data = {}
                    for item in address_vals:
                        for key, value in addresses.items():
                            val = value.pop(item, '')
                            address_data[f'{key}_{item}'] = val
                    instance_id_field = f'{temp.checkout_instance_type}_id'
                    instance_date_field = f'{temp.checkout_instance_type}_date'
                    instance_id = instance[instance_id_field]
                    instance_date = instance[instance_date]
                    data = {
                        **addresses,
                        **address_data,
                        'timeout': 10000,
                        'parcels': [
                            parcels
                        ],
                        'delcared_value': 0,
                        'custom_order_number': instance_id,
                        'service_level_code': 'ECO',
                        'provider_slug': 'RAM',
                        'collection_min_date': instance_date,
                        'collection_after': '08:00',
                        'collection_before': '16:00',
                    }
                    serializer = external_api_serializers.BobGoCheckoutSerializer(data=data)
                    if serializer.is_valid(raise_exception=True):
                        courier_shipment_request = requests.post(url=url, data=serializer.data, headers=settings.BOBGO_DEFAULT_HEADERS)
                        if courier_shipment_request.status_code == '201':
                            courier_shipment_request_data = courier_rate_request.json()
                            if courier_shipment_request_data['submission_status'] == 'success':
                                shipping_tracking_id = courier_shipment_request_data['provider_tracking_reference']
                                temp.checkout_instance.shipping_tracking_id = shipping_tracking_id
                                temp.checkout_instance.save()