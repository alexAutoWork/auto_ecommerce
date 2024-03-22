from rest_framework import serializers
from . utils import upload_to_images, upload_to_html
from . import models

class JSONImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField()

    class Meta:
        model = models.JSONImageModel
        fields = ['image_url']

# class HTMLEmailSerializer(serializers.ModelSerializer):
#     html_file = serializers.FileField()

#     class Meta:
#         model = models.HTMLEmailModel
#         fields = ['html_file']

class HTMLEmailSerializer(serializers.Serializer):
    type_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    filename = serializers.CharField()
    html_template_type = serializers.CharField()
    subject = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    needs_render = serializers.BooleanField(default=True)