from ..auth import auth_model_serializers, auth_models, auth_views
from ..reg import reg_model_serializers, reg_models, reg_views
from ..standard import st_model_serializers, st_models, st_views
from . import admin_mixin_views
from .. import mixins as custom_mixins
from rest_framework.decorators import action
import re
import inspect
from django.core.cache import cache

class UniversalAdminMixin(
    auth_views.OrdersViewSet, auth_views.InvoicesViewSet, auth_views.RepairsViewSet, auth_views.ReturnsViewSet, st_views.ProductsViewSet, admin_mixin_views.ProductStocksViewSet, admin_mixin_views.ProductModelsViewSet, st_views.BrandsViewSet, st_views.CategoriesViewSet, reg_views.UserAddressViewSet, reg_views.UserDetailsViewSet, custom_mixins.CommunicationViewSetMixin, custom_mixins.DefaultCacheMixin
):

    MRO_LIST = ['auth_views.OrdersViewSet', 'auth_views.InvoicesViewSet', 'auth_views.RepairsViewSet', 'auth_views.ReturnsViewSet', 'st_views.ProductsViewSet', 'admin_mixin_views.ProductStocksViewSet', 'admin_mixin_views.ProductModelsViewSet', 'st_views.BrandsViewSet', 'st_views.CategoriesViewSet', 'reg_views.UserAddressViewSet', 'reg_views.UserDetailsViewSet']

    item_type = None
    item_id_field = None

    def return_parent(self, **kwargs):
        '''
        return super() of MRO class specified, according to item type
        for example:
            if item_type == 'invoice':
                return prev. MRO class super(auth_views.OrdersViewSet, self)
        '''
        # item_type = kwargs.get('item_type').capitalize()
        item_type = kwargs.get('item_type')
        for i, elem in enumerate(self.MRO_LIST):
            if item_type in elem:
                mro_index = i - 1
        string = self.MRO_LIST[mro_index].split('.')
        module = string[0]
        module = globals()[module]
        if mro_index != 0:
            parent_class = super(getattr(module, string[1]), self)
        else:
            parent_class = super()
        return parent_class

    def admin_mixin_mro(self):
        '''
        provides a custom actions list to exclude on Django Initialization
        '''
        custom_actions_list = []
        for item in self.MRO_LIST:
            parent = self.return_parent(item_type=item)
            custom_actions = getattr(parent, 'custom_actions', None)
            if custom_actions is not None:
                for action in custom_actions:
                    action = action.replace('_', '-')
                    custom_actions_list.append(action)
        return custom_actions_list

    def retrieve(self, pk=None, **kwargs):
        '''
        provides data from the retrieve function based on item specified
        '''
        parent = return_parent(item_type=self.item_type)
        retrieve = self.get_custom_global_attr(parent, 'retrieve')
        setattr(parent, 'is_admin_req', True)
        data = retrieve(pk=pk)
        return data

    def get_custom_global_attr(self, parent, var):
        '''
        just the getattr function lmao
        '''
        return getattr(parent, var, None)

    def get_global_attr(self, parent, item_hierachy='parent'):
        '''
        provides global serializer + model attributes from item specified
        '''
        model = self.get_custom_global_attr(parent, f'{item_hierachy}_model')
        serializer = self.get_custom_global_attr(parent, f'{item_hierachy}_serializer')
        return [model, serializer]

    def fetch_qs(self, **kwargs):
        '''
        fetch queryset from item specified
        '''
        item_type = kwargs.get('item_type', None)
        item_hierachy = kwargs.get('item_hierachy', 'parent')
        parent = kwargs.get('parent', self.return_parent(item_type=item_type))
        global_attr = self.get_global_attr(parent, item_hierachy)
        select_related = kwargs.get('select_related', [])
        prefetch_related = kwargs.get('prefetch_related', [])
        filter_params = kwargs.get('filter_params', {})
        model_data = global_attr[0].objects.prefetch_related(*prefetch_related).select_related(*select_related).filter(**filter_params)
        unserialized = kwargs.get('unserialized', False)
        if unserialized:
            data = model_data
        else:
            serializer = global_attr[1](model_data, many=True)
            data = serializer.data
        return data

    def fetch_main(self, pk=None, **kwargs):
        '''
        fetch main elements of item specified, including items from retrieve(), communication history and fk items using fetch_related()
        '''
        data = {}
        main = self.retreive(pk=pk)
        data.update(**main[0])
        parent = self.return_parent(item_type=self.item_type)
        self.item_id_field = self.get_custom_global_attr(parent, 'parent_id_field')
        comm_history = kwargs.get('comm_history', False)
        if comm_history:
            pk_filter = {self.item_id_field: pk}
            comm_history = self.fetch_qs(parent=parent, item_hierachy='comm_history', filter_params=pk_filter)
            data.update(**{f'{self.item_type}_comm_history': comm_history})
        related = kwargs.get('related', None)
        if related is not None:
            related_data = self.fetch_related(pk=pk, related=related, main_model=main[1])
            data.update(**related_data)
        return data

    def fetch_related(self, pk=None, **kwargs):
        '''
        fetch items specified by fk relation, child relation, or reverse relation
        '''
        data = {}
        related = kwargs.get('related', None)
        main_model = kwargs.get('main_model', None)
        if related is not None:
            for key, value in related.items():
                if re.search('comm_history', key):
                    item.split('_', 1)
                    value['item_type'] = item[0]
                    value['item_hierachy'] = item[1]
                else:
                    value['item_type'] = key
                value['filter_params'].append(**{self.item_id_field: pk})
                parent = self.return_parent(item_type=key)
                value['parent'] = parent
                if value['item_hierachy'] == 'child':
                    parent_select_related = value.pop('parent_select_related', None)
                    child_data = self.fetch_qs(**value, unserialized=True)
                    parent_id_field = self.get_custom_global_attr(parent, 'parent_id_field')
                    value['filter_params'] = {parent_id_field: self.get_custom_global_attr(child_data, parent_id_field).pk}
                    if parent_select_related is not None:
                        value['select_related'] = parent_select_related
                    else:
                        value.pop('select_related')
                if value['item_hierachy'] == 'reverse':
                    parent_id_field = kwargs.get('parent_id_field', self.get_custom_global_attr(parent, 'parent_id_field'))
                    if main_model is not None:
                        value['filter_params'] = {parent_id_field: self.get_custom_global_attr(main_model, parent_id_field).pk}
                value.pop('item_hierachy')
                data.append(**{key: self.fetch_qs(**value)})
            return data
            
    def fetch_list(self, **kwargs):
        '''
        literally fetch queryset of items specified
        '''
        data = {}
        items = kwargs.get('items', None)
        if items is not None:
            for key, value in items.items():
                value['item_type'] = key
                data.append(**{key: self.fetch_qs(**value)})
            return data

    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None, **kwargs):
        '''
        update status of applicable items
        '''
        item_type = request.data.get('item_type', None)
        if item_type is not None:
            parent = self.return_parent(item_type=item_type)
            model = self.get_global_attr(parent)[0]
            instance = model.objects.get(pk=pk)
            data = {
                'comm_method': request.data.get('comm_method'),
                'current_status_id': request.data.get('status_id'),
                'subject': request.data.get('subject'),
                'comment': request.data.get('comment')
            }
            return super().update_status(request, is_admin_req=True, **data)

    @action(detail=True, methods=['put'])
    def create_comm(self, request, pk=None):
        '''
        create communication item of applicable items
        '''
        item_type = request.data.get('item_type', None)
        if item_type is not None:
            parent = self.return_parent(item_type=item_type)
            global_attr = self.get_global_attr(parent)
            model = global_attr[0]
            instance = model.objects.get(pk=pk)
            comm_history_serializer = self.get_custom_global_attr(parent, 'comm_history_serializer')
            comm_object_data = {
                'subject': request.data.get('subject'),
                'comment': request.data.get('comment')
            }
            comm_object_data['serializer_data'] = comm_object_data
            comm_object_data.append(**{'type_id': pk, 'user_id': instance.user_id, 'comm_history_serializer': comm_history_serializer})
            super().initialize_comm_object(request, is_admin_req=True, **comm_object_data)
            comm_method = request.data.get('comm_method', None)
            return super().check_method(comm_method)

    def create(self, request, **kwargs):
        '''
        create item with applicable permissions
        '''
        item_type = request.data.get('item_type', None)
        if item_type is not None:
            for item in item_type:
                data = request.data.get(item, None)
                if data is not None:
                    parent = self.return_parent(item_type=item)
                    global_attr = self.get_global_attr(parent)
                    serializer = global_attr[1](data=data)
                    if serializer.is_valid(raise_exception=True):
                        return serializer.save()

    def destroy(self, request, pk=None):
        '''
        delete item with applicable permissions
        - starts by physically deleting instance
        if fails, falls back on:
            - setting 'is_active' to False
            if fails again, send an error message
        '''
        item_type = request.data.get('item_type', None)
        if item_type is not None:
            parent = self.return_parent(item_type=item_type)
            global_attr = self.get_global_attr(parent)
            model = global_attr[0](data=data)
            instance = model.objects.get(pk=pk)
            if instance is not None:
                try:
                    instance.delete()
                    message = f'{item_type} successfully deleted'
                    status = status.HTTP_202_ACCEPTED
                except ProtectedError:
                    field = None
                    try:
                        instance.is_active = False
                        instance.save()
                        message = f'{item_type} successfully marked as inactive'
                        status = status.HTTP_202_ACCEPTED
                    except FieldDoesNotExist:
                        message = f'{item_type} was unable to be deleted'
                        status = status.HTTP_400_BAD_REQUEST
                instance.refresh_from_db()
                return Response({'message': message}, status=status)