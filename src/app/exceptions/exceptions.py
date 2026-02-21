class AppExceptions(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class LLMInvalidJSONError(AppExceptions):
    def __init__(self):
        super().__init__(message="LLM returned invalid JSON", status_code=502)


class LLMInvalidValidationError(AppExceptions):
    def __init__(
        self,
    ):
        super().__init__(message="LLM returned invalid Pydantic Model", status_code=502)


class LLM_API_Error(AppExceptions):
    def __init__(self, api_status_code):
        self.api_status_code = api_status_code
        super().__init__(message="LLM API service unavailable", status_code=502)
