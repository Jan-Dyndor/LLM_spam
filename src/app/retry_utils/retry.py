import requests

from app.exceptions.exceptions import (
    LLMError,
    LLMInvalidJSONError,
    LLMInvalidValidationError,
)

retryable_status_codes = [408, 429, 500, 502, 503, 504]


def should_retry(exception: BaseException) -> bool:
    if isinstance(exception, requests.Timeout):
        return True
    elif isinstance(exception, requests.ConnectionError):
        return True
    elif isinstance(exception, LLMError):
        return True
    elif isinstance(exception, LLMInvalidJSONError):
        return True
    elif isinstance(exception, LLMInvalidValidationError):
        return True
    elif isinstance(exception, requests.HTTPError):
        status_code = exception.response.status_code
        if status_code in retryable_status_codes:
            return True
        else:
            return False
    else:
        return False
