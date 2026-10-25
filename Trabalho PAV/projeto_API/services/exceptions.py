class APIError(Exception):
    status_code = 500


class InvalidDataError(APIError, ValueError):
    status_code = 422


class ResourceNotFoundError(APIError, LookupError):
    status_code = 404


class ResourceConflictError(APIError, ValueError):
    status_code = 409
