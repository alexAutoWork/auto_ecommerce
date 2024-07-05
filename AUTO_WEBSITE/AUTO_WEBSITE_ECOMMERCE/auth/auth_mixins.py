from rest_framework import permissions

EDIT_METHODS = ('PUT', 'PATCH')

class ChildObjectAuthUserViewSetMixin():
    model_parent = None
    model_parent_id = None
    child_model = None
    field_name = None

    def get_parent_queryset(self, request):
        user_id = request.user.user_id
        model_parent_id = request.query_params[self.model_parent_id]
        # field_name = self.model_parent_id
        # field_name_iexact = field_name + '__iexact'
        if self.model_parent.objects.filter(**{str(self.field_name): model_parent_id}, user_id=user_id).exists():
            return True

    def get_child_queryset(self, request, **kwargs):
        self.get_parent_queryset(request)
        if True:
            user_id = request.user.user_id
            model_parent_id = request.query_params[self.model_parent_id]
            if kwargs is not None:
                prefetch_related_field = kwargs.pop('prefetch_related')
                queryset = self.child_model.objects.prefetch_related(prefetch_related_field).filter(**{str(self.field_name): model_parent_id})
            # field_name = self.model_parent_id
            # field_name_iexact = field_name + '__iexact'
            else:
                queryset = self.child_model.objects.filter(**{str(self.field_name): model_parent_id})
            # queryset = self.child_model.objects.filter(**{str(self.field_name): model_parent_id})
            return queryset

class ChildObjectAuthUserPermissionMixin(ChildObjectAuthUserViewSetMixin):

    def has_child_object_permission(self, request):
        queryset = super().get_child_queryset(request)
        if queryset.exists():
            return True
        else:
            return False
    # def has_child_object_permission_edit_or_delete(self, request):
    #     super().get_parent_queryset(request)
    #     if True:
    #         return super().get_child_queryset(request)
    #     return False