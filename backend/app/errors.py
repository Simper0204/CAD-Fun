from typing import Any


class APIError(Exception):
    """Error that maps directly onto the documented ErrorResponse body."""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or []

    def to_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.details:
            body["details"] = self.details
        return body


class QuestionNotFound(Exception):
    def __init__(self, question_id: str) -> None:
        super().__init__(question_id)
        self.question_id = question_id


class QuestionConfigError(Exception):
    """The stored question cannot be scored. This is a server-side fault."""

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or []


def sanitize_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep validation details JSON-serializable and free of raw input values."""
    sanitized: list[dict[str, Any]] = []
    for error in errors:
        sanitized.append(
            {
                "loc": [str(part) for part in error.get("loc", ())],
                "msg": str(error.get("msg", "")),
                "type": str(error.get("type", "")),
            }
        )
    return sanitized
