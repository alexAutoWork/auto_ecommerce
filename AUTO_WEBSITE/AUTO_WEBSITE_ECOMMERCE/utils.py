import json
import datetime
import re
import os
import io
from rest_framework.parsers import JSONParser

def return_date_and_time():
    date = datetime.datetime.now()
    return f'{date.day}-{date.month}-{date.year} {date.hour}:{date.minute}:{date.second}'

def upload_to_images(filename):
    return 'images/{filename}'.format(filename=filename)

def upload_to_html(filename):
    return 'html/{filename}'.format(filename=filename)

def generate_filename(keyword_1, keyword_2, datetime):
    datetime = re.sub('[- :]', '_', datetime)
    return f'{keyword_1}_{keyword_2}_{datetime}'

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