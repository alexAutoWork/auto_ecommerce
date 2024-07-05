from rest_framework import serializers

class SerializerOrPkField(serializers.Field):
    pk_field = None
    alt_field = None

    def __init__(self, **kwargs):
        queryset = kwargs.pop('queryset')
        alt_field = kwargs.pop('alt_field')
        alt_field_params = kwargs.pop('alt_field_params', None)
        default = {'read_only': True}
        if alt_field_params is not None:
            alt_field_params = {**alt_field_params, **default}
        else:
            alt_field_params = default
        self.pk_serializer = serializers.PrimaryKeyRelatedField(queryset=queryset)
        self.alt_field = alt_field(**alt_field_params)
        super().__init__()

    def to_internal_value(self, data):
        method = self.parent.context['request'].method
        if method in ['POST']:
            return self.pk_field.to_internal_value(data)
        else:
            return self.alt_field.to_representation(value)

    def to_representation(self, value):
        method = self.parent.context['request'].method
        if method in ['POST']:
            return self.pk_field.to_representation(value)
        else:
            return self.alt_field.to_representation(value)