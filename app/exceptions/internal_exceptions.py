from torpedo.exceptions import BaseSanicException
from torpedo.exceptions import BadRequestException, NotFoundException

class ResourceNotFoundException(BaseSanicException):
    pass

class NoSendAddressFoundException(BaseSanicException):
    pass

class AppNotConfigured(BaseSanicException):
    pass
class ForbiddenException(BadRequestException):
    def __init__(
        self,
        error,
        status_code=403,
    ):
        super().__init__(error, status_code)
        
class UnAuthorizeException(BadRequestException):
    def __init__(
        self,
        error,
        status_code=401,
    ):
        super().__init__(error, status_code)
        
class ResourceConflictException(BadRequestException):
    pass

class RequiredParamsException(BadRequestException):
    pass

class InvalidParamsException(BadRequestException):
    pass

class ValidationError(BadRequestException):
    pass