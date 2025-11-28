"""
Custom exception classes for SYNAPSE API.

Provides specific exception types for common error scenarios:
- Database errors (not found, conflict, FK violation)
- Validation errors
- Business logic errors
- External service errors
"""

from typing import Any


class SynapseException(Exception):
    """Base exception for all SYNAPSE errors"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


# ============================================================================
# Database Exceptions
# ============================================================================


class DatabaseError(SynapseException):
    """Base for all database-related errors"""

    pass


class NotFoundError(DatabaseError):
    """Resource not found in database (404)"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, {"resource_type": resource_type, "id": resource_id})


class DuplicateError(DatabaseError):
    """Duplicate resource violation (409 Conflict)"""

    def __init__(self, resource_type: str, field: str, value: str):
        message = f"{resource_type} with {field}='{value}' already exists"
        super().__init__(message, {"resource_type": resource_type, "field": field, "value": value})


class ForeignKeyError(DatabaseError):
    """Foreign key constraint violation (400)"""

    def __init__(self, field: str, referenced_id: str):
        message = f"Referenced {field} '{referenced_id}' does not exist"
        super().__init__(message, {"field": field, "referenced_id": referenced_id})


# ============================================================================
# Validation Exceptions
# ============================================================================


class ValidationError(SynapseException):
    """Input validation error (400/422)"""

    def __init__(self, field: str, message: str):
        super().__init__(f"Validation error on '{field}': {message}", {"field": field})


class FileValidationError(ValidationError):
    """File upload validation error"""

    def __init__(self, filename: str, message: str):
        super().__init__("file", f"File '{filename}' invalid: {message}")


# ============================================================================
# Business Logic Exceptions
# ============================================================================


class BusinessLogicError(SynapseException):
    """Business rule violation (400)"""

    pass


class InactiveResourceError(BusinessLogicError):
    """Resource is inactive/disabled (403)"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} '{resource_id}' is inactive"
        super().__init__(message, {"resource_type": resource_type, "id": resource_id})


class RuleExecutionError(BusinessLogicError):
    """Error during rule execution"""

    def __init__(self, rule_id: str, error_message: str):
        message = f"Rule '{rule_id}' execution failed: {error_message}"
        super().__init__(message, {"rule_id": rule_id, "error": error_message})


# ============================================================================
# External Service Exceptions
# ============================================================================


class ExternalServiceError(SynapseException):
    """Error from external service/API"""

    def __init__(self, service_name: str, error: str):
        message = f"External service '{service_name}' error: {error}"
        super().__init__(message, {"service": service_name, "error": error})
