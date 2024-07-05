from rest_framework import serializers
from . utils import upload_to_images, upload_to_html
from . import models

class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
    file_type = serializers.CharField()
    user_type = serializers.CharField()
    instance_type = serializers.CharField()
    instance_id = serializers.CharField(required=False, allow_blank=True)

class HTMLEmailSerializer(serializers.Serializer):
    type_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    obj_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    filename = serializers.CharField()
    html_template_type = serializers.CharField()
    subject = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    needs_render = serializers.BooleanField(default=True)

class NestedSerializer(serializers.ModelSerializer):
    nested_fields = None
    def to_representation(self, instance):
        repre = super().to_representation(instance)
        request = self.context['request']
        context = {'request': request}
        method = request.method
        is_data = self.context.get('is_data', False)
        if method not in ['POST']:
            if self.nested_fields is not None:
                for key, value in self.nested_fields.items():
                    repre.pop(key)
                    attr = getattr(instance, key)
                    if is_data:
                        serializer = value(data=attr, context=context)
                        serializer.is_valid()
                    else:
                        serializer = value(attr, context=context)
                    repre[key] = serializer.data
        return repre