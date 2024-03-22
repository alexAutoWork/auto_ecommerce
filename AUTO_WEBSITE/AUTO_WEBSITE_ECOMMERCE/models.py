from .reg.reg_models import UserLogin
from .reg.reg_backends import EmailBackend
from django.db import models
from . import utils

class JSONImageModel(models.Model):
    image_url = models.ImageField(upload_to=utils.upload_to_images)

    class Meta:
        managed = False

# class HTMLEmailModel(models.Model):
#     html_file = models.FileField(upload_to=utils.upload_to_html)

#     class Meta:
#         managed = False