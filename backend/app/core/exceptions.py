from typing import Any


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: list[dict[str, Any]] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed", details: list[dict[str, Any]] | None = None):
        super().__init__("AUTHENTICATION_ERROR", message, 401, details)


class InvalidCredentialsError(AuthenticationError):
    def __init__(self):
        super().__init__("Invalid email or password", [{"code": "INVALID_CREDENTIALS"}])


class TokenExpiredError(AuthenticationError):
    def __init__(self):
        super().__init__("Token has expired", [{"code": "TOKEN_EXPIRED"}])


class AccountLockedError(AuthenticationError):
    def __init__(self, locked_until: str):
        super().__init__(
            f"Account locked until {locked_until}",
            [{"code": "ACCOUNT_LOCKED", "locked_until": locked_until}],
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Insufficient permissions", details: list[dict[str, Any]] | None = None):
        super().__init__("AUTHORIZATION_ERROR", message, 403, details)


class InsufficientPermissionsError(AuthorizationError):
    def __init__(self):
        super().__init__("You do not have permission to perform this action")


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: list[dict[str, Any]] | None = None):
        super().__init__("VALIDATION_ERROR", message, 422, details)


class NotFoundError(AppException):
    def __init__(self, entity: str, entity_id: str = ""):
        msg = f"{entity} not found" + (f": {entity_id}" if entity_id else "")
        super().__init__("NOT_FOUND", msg, 404)
        self.entity = entity
        self.entity_id = entity_id


class ConflictError(AppException):
    def __init__(self, message: str, details: list[dict[str, Any]] | None = None):
        super().__init__("CONFLICT_ERROR", message, 409, details)


class BusinessRuleError(AppException):
    def __init__(self, message: str, code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(code, message, 422)


class ExternalServiceError(AppException):
    def __init__(self, service: str, message: str):
        super().__init__("EXTERNAL_SERVICE_ERROR", f"{service}: {message}", 502)
