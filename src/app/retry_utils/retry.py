import requests

from app.exceptions.exceptions import (
    LLM_API_Error,
    LLMInvalidJSONError,
    LLMInvalidValidationError,
)

# -1 is to retry when API somehow returned empty response to retry it
retryable_status_codes = [-1, 408, 429, 500, 502, 503, 504]


def should_retry(exception: BaseException) -> bool:
    if isinstance(exception, requests.Timeout):
        return True
    elif isinstance(exception, requests.ConnectionError):
        return True
    elif isinstance(exception, LLM_API_Error):
        if exception.api_status_code in retryable_status_codes:
            return True
        else:
            return False
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
