from rest_framework import viewsets, status, views, permissions
from django.conf import settings
from . import external_api_serializers
import hashlib, urllib.parse, base64, requests
from socket import gethostbyname_ex
from ..reg.reg_models import UserLogin, UserDetails
from ..auth.auth_models import Invoices, InvoiceItems
from ..auth.auth_model_serializers import InvoicesSerializer, InvoiceItemsSerializer
from ..standard import st_models
from .. import utils

class PayfastPayment(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def generate_signature(self, data_array, pass_phrase = ''):
        payload = ''
        for key in data_array:
            payload += key + '=' + urllib.parse.quote_plus(data_array[key].replace('+', ' ')) + '&'
        payload = payload[:-1]
        if pass_phrase != '':
            payload += f'&passphrase={pass_phrase}'
        return hashlib.md5(payload.encode()).hexdigest()

    def initialize_data(self, request, session):
        user = self.request.user
        user_details = UserDetails.objects.filter(user_id=user).select_related('user_id').values('name', 'surname', 'email', 'mobile_no')
        order_details = request.session.get('order_details_instance')
        data = {
            'merchant_id': '10032658',
            'merchant_key': 'fttplevgghpgv',
            'return_url': 'example',
            'cancel_url': 'example',
            'notify_url': 'example',
            'name_first': user_details['name'],
            'name_last': user_details['surname'],
            'email_address': user_details['email'],
            'cell_number': user_details['mobile_no'],
            'amount': order_details['order_total'],
            'confirmation_address': user_details['email'],
        }
        pass_phrase = 'extinct_parched_ember_cofounder'
        data['security_signature'] = self.generate_signature(data, pass_phrase)
        request.session['initialized_data'] = data
        serializer = external_api_serializers.PayFastSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def recieve_incoming_data(self, request):
        serializer = external_api_serializers.PayFastIncomingSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            request.session['incoming_data'] = data
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
        return (data.get('signature') == signature)

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
            return False
        else:
            return True

    def validate_payment_data(self, request, session, data):
        initialized_data = request.session.get('initialized_data')
        amount = initialized_data['amount']
        amount_gross = data.get('amount_gross')
        return not (abs(amount) - amount_gross) > 0.01

    def validate_server_confirmation(self, param_string, host = 'sandbox.payfast.co.za'):
        url = f'https://{host}/eng/query/validate'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, data=param_string, headers=headers)
        return response.text == 'VALID'

class SageAccountingIntegration(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
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

    def get_customer(self, request, user_id):
        user_details = UserDetails.objects.filter(user_id=user_id).values('sage_id')
        if user_details is not None:
            params = f'{user_details}'
            get_customer_request = self.send_request(data=None, service_name='Customer', method_name='Get', **params)
            if get_customer_request.status_code != '200' or '202':
                self.save_customer(user_id=user_id)
                self.get_customer(user_id=user_id)
            else:
                return True

    def save_customer(self, request, user_id):
        user_details_object = UserDetails.objects.filter(user_id=user_id).select_related('user_id')
        user_details_values = user_details_object.values('name', 'surname', 'company', 'vat_no', 'email', 'mobile_no', 'is_verified')
        if 'is_verified' == True:
            contact_name = user_details_values['name'] + user_details_values['surname']
            if user_details_values['company'] is None:
                company_name = contact_name
            else:
                company_name = user_details_values['company']
            data = {
                'Name': company_name,
                'TaxReference': user_details_values['vat_no'],
                'Mobile': user_details_values['mobile_no'],
                'Email': user_details_values['email'],
                'ContactName': contact_name
            }
            serializer = external_api_serializers.SageCustomerSerializer(data=data)
            params = 'Save'
            save_customer_request = self.send_request(data=serializer.data, service_name='Customer', method_name='Save', **params)
            if save_customer_request.status_code == '201':
                save_customer_request_data = utils.deserialize(save_customer_request.json())
                deserializer = external_api_serializers.SageCustomerSerializer(data=save_customer_request_data)
                if deserializer.is_valid():
                    sage_customer_details = deserializer.validated_data
                    sage_id = sage_customer_details['CustomerId']
                    return user_details_object.update(sage_id=sage_id, is_synced=True)

    def get_invoice(self, request, invoice_id):
        invoice_details = Invoices.objects.filter(invoice_id=invoice_id).values('sage_id')
        if invoice_details is not None:
            params = f'{invoice_details}'
            get_invoice_request = self.send_request(data=None, service_name='TaxInvoice', method_name='Get', **params)
            if get_invoice_request.status_code != '200' or '202':
                self.save_invoice(invoice_id=invoice_id)
                self.get_invoice(invoice_id=invoice_id)
            else:
                return True

    def save_invoice(self, request, invoice_id, customer_id):
        invoice_items_object = InvoiceItems.objects.filter(invoice_id=invoice_id)
        invoice_items_first_object = invoice_items_object.first().select_related('invoice_id__order_id').values('order_id', 'order_date', 'order_subtotal', 'order_tax', 'order_total')
        order_id = invoice_items_first_object['order_id']
        invoice_items_after_objects = invoice_items_object.prefetch_related('order_item_id__sku_no__product_config_id').values('order_item_price', 'sage_item_code', 'sku_no')
        invoice_items_list = []
        for item in invoice_items_after_objects:
            invoice_items_dict = {
                'SelectionId': item['sage_item_code'],
                'Description': item['sku_no'],
                'Exclusive': item['order_item_price'],
                'Quantity': 1
            }
            invoice_items_list.append(invoice_items_dict)
        data = {
            'CustomerId': customer_id,
            'Date': invoice_items_first_object['order_date'],
            'Reference': f'{order_id} [{invoice_id}]',
            'Exclusive': invoice_items_first_object['order_subtotal'],
            'Tax': invoice_items_first_object['order_tax'],
            'Total': invoice_items_first_object['order_total'],
            'Lines': invoice_items_list
        }
        serializer = external_api_serializers.SageInvoiceSerializer(data=data)
        save_invoice_request = self.send_request(data=serializer.data, service_name='TaxInvoice', method_name='Save')
        if save_invoice_request.status_code == '201':
            save_invoice_request_data = utils.deserialize(save_invoice_request.json())
            deserializer = external_api_serializers.SageInvoiceSerializer(data=save_invoice_request_data)
            if deserializer.is_valid():
                sage_invoice_details = deserializer.validated_data
                sage_id = sage_invoice_details['InvoiceId']
                sage_doc_no = sage_invoice_details['DocumentNumber']
                return invoice_items_first_object.update(is_synced=True, sage_id=sage_id, sage_doc_no=sage_doc_no)

    def get_item(self, request, products_id):
        item_details = st_models.ProductConfig.objects.filter(products_id=products_id).values('sage_id')
        if item_details is not None:
            params = f'{item_details}'
            get_item_request = self.send_request(data=None, service_name='Item', method_name='Get', **params)
            if get_item_request.status_code != '200' or '202':
                self.save_item(products_id=products_id)
                self.get_item(products_id=products_id)
            else:
                return True

    def save_item(self, request, products_id):
        item_details_object = st_models.ProductConfig.objects.filter(products_id=products_id).select_related('products_id', 'variation_id')
        item_details_values = item_details_object.values('name', 'value', 'price', 'sage_item_code')
        name = item_details_values['name']
        variation = item_details_values['value']
        description = f'{name} {variation}'
        data = {
            'Code': item_details_values['sage_item_code'],
            'Description': description,
            'PriceExclusive': item_details_values['price']
        }
        serializer = external_api_serializers.SageItemSerializer(data=data)
        save_item_request = self.send_request(data=serializer.data, service_name='Item', method_name='Save')
        if save_item_request.status_code == '201':
            save_item_request_data = utils.deserialize(save_item_request.json())
            deserializer = external_api_serializers.SageItemSerializer(data=save_item_request_data)
            if deserializer.is_valid():
                sage_item_details = deserializer.validated_data
                sage_id = sage_item_details['ItemId']
                return item_details_object.update(sage_id=sage_id, is_synced=True)
