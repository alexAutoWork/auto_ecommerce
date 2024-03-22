from rest_framework import permissions
from . import auth_utils, auth_mixins

EDIT_METHODS = ('PUT', 'PATCH')
TYPE_1_METHODS = ('GET', 'OPTIONS', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE')
TYPE_2_METHODS = ('GET', 'OPTIONS', 'HEAD', 'POST', 'PATCH')
TYPE_3_METHODS = ('GET', 'OPTIONS', 'HEAD', 'PATCH')
TYPE_4_METHODS = ('GET', 'OPTIONS', 'HEAD', 'POST')

class BaseAuthUserPermission(auth_mixins.ChildObjectAuthUserPermissionMixin, permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

        if request.user.get('is_verified') == True:
            return True
        return False

    def has_object_permission(self, request, view, obj):

        if request.type in permissions.SAFE_METHODS:
            if obj.user_id == request.user:
                return True
            else:
                self.has_child_object_permission()
            return False

        if request.type == 'POST':
            return True
            # if obj.owner == request.user:
            #     return True
            # return False

        if request.type in EDIT_METHODS or request.type == 'DELETE':
            if obj.user_id == request.user:
                return True
            else:
                self.has_child_object_permission_edit_or_delete()
            return False

        return False

    def has_child_object_permission(self, request, view, obj):

        if request.type in permissions.SAFE_METHODS:
            get_parent_queryset(request, model_parent_id, field_parent_id, model_parent)
            if True:
                get_child_queryset(request, model_parent_id, field_parent_id, model_parent)
            return False

    def has_child_object_permission_edit_or_delete(self, request, view, obj):

        if request.type in EDIT_METHODS or request.type == 'DELETE':
            get_parent_queryset(request, model_parent_id, field_parent_id, model_parent)
            if True:
                get_child_queryset(request, model_parent_id, field_parent_id, model_parent)
            return False
        
class ObjectAuthUserPermission(auth_mixins.ChildObjectAuthUserPermissionMixin, permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False
        
        if request.user.get('is_verified') == True:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        
        if request.type in permissions.SAFE_METHODS:
            if obj.user_id == request.user:
                return True
            else:
                self.has_child_object_permission()
            return False

        if request.type == 'POST':
            return True
            # if obj.owner == request.user:
            #     return True
            # return False

        return False

    def has_child_object_permission(self, request, view, obj):

        if request.type in permissions.SAFE_METHODS:
            get_parent_queryset(request, model_parent_id, field_parent_id, model_parent)
            if True:
                get_child_queryset(request, model_parent_id, field_parent_id, model_parent)
            return False

class SystemObjectAuthUserPermission(auth_mixins.ChildObjectAuthUserPermissionMixin, permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

        if request.user.get('is_verified') == True:
            return True
        return False

    def has_object_permission(self, request, view, obj):

        if request.type in permissions.SAFE_METHODS:
            if obj.user_id == request.user:
                return True
            else:
                self.has_child_object_permission()
        return False

    def has_child_object_permission(self, request, view, obj):

        if request.type in permissions.SAFE_METHODS:
            get_parent_queryset(request, model_parent_id, field_parent_id, model_parent)
            if True:
                get_child_queryset(request, model_parent_id, field_parent_id, model_parent)
            return False
