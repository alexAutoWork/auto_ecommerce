from rest_framework import permissions

EDIT_METHODS = ('PUT', 'PATCH')

class ChildObjectAuthUserPermissionMixin():
    def has_child_object_permission(self, request, view, obj):
        if request.type in permission.SAFE_METHODS:
            SystemObjectAuthUserViewSetMixin.get_parent_queryset(request, model_parent_id, field_parent_id, model_parent)
            if True:
                SystemObjectAuthUserViewSetMixin.get_child_queryset(request, model_parent_id, field_parent_id, model_parent, model_serializer)
            return False

    def has_child_object_permission_edit_or_delete(self, request, view, obj):
        if request.type == EDIT_METHODS or request.type == 'DELETE':
            SystemObjectAuthUserViewSetMixin.get_parent_queryset(request, model_parent_id, field_parent_id, model_parent)
            if True:
                SystemObjectAuthUserViewSetMixin.get_child_queryset(request, model_parent_id, field_parent_id, model_parent, model_serializer)
            return False

class ChildObjectAuthUserViewSetMixin():
    def get_parent_queryset(self, request, model_parent_id, field_parent_id, model_parent):
        user_id = self.request.user
        model_parent_id = self.request.data[model_parent_id]
        field_name = field_parent_id
        field_name_iexact = field_name + '__iexact'
        if model_parent.objects.filter(**{field_name_iexact: model_parent_id}, user_id=user_id).exists():
            return True

    def get_child_queryset(self, request, model_parent_id, field_parent_id, model_parent, model_serializer):
        user_id = self.request.user
        model_parent_id = self.request.data[model_parent_id]
        field_name = field_parent_id
        field_name_iexact = field_name + '__iexact'
        queryset = model_parent.objects.filter(**{field_name_iexact: model_parent_id})
        serializer = model_serializer(data=queryset, many=True)
        return serializer.data