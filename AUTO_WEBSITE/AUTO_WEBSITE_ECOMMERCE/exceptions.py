from rest_framework.exceptions import APIException

class CustomAPIException(APIException):
    status_code = None
    default_detail = None
    default_code = None
    def __init__(self, **kwargs):
        self.status_code = kwargs.get('status_code')
        self.default_detail = kwargs.get('detail')
        self.default_code = kwargs.get('code')

class UserSyntaxError(CustomAPIException):
    def __init__(self, **kwargs):
        kwargs['status_code'] = 400
        super().__init__(**kwargs)

    def invalid(self, obj_type):
        detail = f'invalid {obj_type}, please try again'
        code = 'invalid_type'
        self.__init__(detail=detail, code=code)

    def none(self, obj_type):
        detail = f'{obj_type} cannot be none'
        code = 'none_not_allowed'
        self.__init__(detail=detail, code=code)

class ServerPayFastError(APIException):
    def __init__(self, **kwargs):
        kwargs['status_code'] = 500
        super().__init__(**kwargs)

    def failure(self, obj_type):
        detail = f'Security check failed'
        code = f'{obj_type}_security_check_failure'
        self.__init__(detail=detail, code=code)

    # def invalid_or_none(self, obj_type):
    #     detail = f'invalid or no {obj_type}'
    #     code = 'invalid_or_none'
    #     self.__init__(detail, code)

# class invalid_error(Exception):
#     def __init__(self, obj_type):
#         self.obj_type = obj_type
#         super().__init__(f'invalid {obj_type}. Try again.')

# class invalid_or_none_error(Exception):
#     def __init__(self, obj_type):
#         self.obj_type = obj_type
#         super().__init__(f'invalid or no {obj_type}')

class no_items_found_error(Exception):
    def __init__(self, obj_type):
        self.obj_type = obj_type
        super().__init__(f'no items found in {obj_type}')

class not_found_error(Exception):
    def __init__(self, obj_type):
        self.obj_type = obj_type
        super().__init__(f'{obj_type} not found. Try Again')

class none_not_allowed_error(Exception):
    def __init__(self, obj_type):
        self.obj_type = obj_type
        super().__init__(f'{obj_type} should not be none')

class item_non_active_error(Exception):
    def __init__(self, obj_type):
        self.obj_type = obj_type
        super().__init__(f'{obj_type} is not active. Try again.')

class item_required_error(Exception):
    def __init__(self, obj_type):
        self.obj_type = obj_type
        super().__init__(f'{obj_type} required. Try again')

class payfast_invalid_error(Exception):
    def __init__(self):
        self.obj_type = obj_type
        super().__init__(f'Invalid {obj_type}, security check failed')