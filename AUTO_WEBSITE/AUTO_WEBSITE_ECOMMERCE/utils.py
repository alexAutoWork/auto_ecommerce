import json
import datetime
import re
import os
import io

from rest_framework.parsers import JSONParser
from decimal import Decimal as dec
from django.conf import settings
from django.core.cache import cache

vat_perc = dec(0.15)

def return_date_and_time():
    date = datetime.datetime.now()
    return f'{date.day}-{date.month}-{date.year} {date.hour}:{date.minute}:{date.second}'

def upload_to_images(filename):
    return 'images/{filename}'.format(filename=filename)

def upload_to_html(filename):
    return 'html/{filename}'.format(filename=filename)

def generate_filename(datetime, **kwargs):
    datetime = re.sub('[- :]', '_', datetime)
    filename = ''
    for key, value in kwargs.items():
        filename += f'{value}_'
    return f'{filename}{datetime}'
    # return f'{keyword_1}_{keyword_2}_{datetime}'

def delete_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)

def image_url_to_json(url):
    image_url_dict = {1: url}
    if key in image_url_dict:
        image_url_dict[key] += 1
        image_url_dict.append({key: url})
    return json.dumps(image_url_dict)

def deserialize(data):
    data_input = io.BytesIO(data)
    data_output = JSONParser().parse(data_input)
    return data_output

def get_fields_overrider(result, field_name):
    field_name = result.pop(str(field_name))
    result['ID'] = field_name
    return result

def calculate_vat(price):
    excl = price
    vat = excl * vat_perc
    vat = round(vat, 2)
    incl = excl + vat
    data = {
        'excl': excl,
        'vat': vat,
        'incl': incl
    }
    return data

# def is_frontend_req(params):
#     # frontend_req = request.query_params.get('frontend_req', False)
#     # frontend_req = request.query_params['frontend_req']
#     if params != 'True' or True:
#         return False
#     else:
#         return True

def return_file(**kwargs):
    return_file = kwargs.get('return_file', False)
    filedir = kwargs.get('filedir', None)
    filename = kwargs.get('filename', None)
    if filename is not None:
        filedir = filedir + filename
    current = os.path.dirname(__file__)
    current = os.path.dirname(current)
    # file = current + '/media' + filedir
    file = filedir
    # file = os.path.join(current, settings.MEDIA_ROOT, filedir)
    print(file)
    if os.path.isfile(file):
        if return_file:
            return file
        return True
    else:
        return False

def create_cache_name(**kwargs):
    model = kwargs.get('model')
    cache_name = f'{model}'
    pk_fields = kwargs.get('pk_fields', None)
    for key, value in pk_fields.items():
        cache_name += f'_{key}={value}'
    return cache_name

def get_or_query_cache(**kwargs):
    delete = kwargs.get('delete', False)
    pk_fields = kwargs.get('pk_fields')
    model = kwargs.get('model')
    cache_name = create_cache_name(pk_fields=pk_fields, model=model)
    if delete:
        return cache.delete(cache_name)
    else:
        qs = kwargs.get('qs')
        queryset = cache.get_or_set(cache_name, qs)
        return queryset

def get_private(**kwargs):
    self = kwargs.get('self')
    attrs = kwargs.get('attrs', None)
    attr_values = []
    if attrs is not None:
        for attr in attrs:
            value = getattr(self, f'_{self.__class__.__name__}' + f'__{attr}', None)
            attr_values.append(value)
    if len(attr_values) == 1:
        attr_values = attr_values[0]
    return attr_values