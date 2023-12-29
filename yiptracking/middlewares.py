from contextlib import suppress
import hashlib
import json
import json
import logging
import traceback

logger = logging.getLogger("django")

class UniversalErrorHandlerMiddleware:
    """
    Middleware for handling exceptions and generating error responses.

    Args:
        get_response: The callable that takes a request and returns a response.

    Methods:
        __call__(self, request): Process the request and return the response.
        log_exception(self, request, exception): Log the exception and request information.
        process_exception(self, request, exception): Process the exception and return a response.

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cache the body
        _ = request.body
        return self.get_response(request)


    def log_exception(self, request, exception):
        """
        Log the exception and prints the information in CLI.

        Args:
            request: The request object.
            exception: The exception object.

        """

        body = request._body.decode("utf-8") if hasattr(request, "_body") else "No body"
        auth = request.auth if hasattr(request, "auth") else "No Auth data"

        with suppress(json.JSONDecodeError):
            body = json.loads(body)
            body = json.dumps(body, indent=4)

        with suppress(json.JSONDecodeError):
            auth = json.dumps(auth, indent=4)
        
        exception_id = self.generate_error_id(exception)
            
        request_info = (
            f"EXCEPTION INFO:\n"
            f"ID: {exception_id}\n"
            f"TYPE: {type(exception).__name__}\n"
            f"MESSAGE: {str(exception)}\n"
            f"METHOD: {request.method}\n"
            f"PATH: {request.path}\n"
            f"AUTH: \n{auth}\n"
            f"BODY: \n{body}\n"
            f"TRACEBACK: {traceback.format_exc()}"
        )
        logger.error(request_info)

        print(request_info)
        
    def generate_error_id(self, exception):
        error_info = f"{type(exception).__name__}: {str(exception)}"

        hash_object = hashlib.sha256(error_info.encode())
        return hash_object.hexdigest()

    def process_exception(self, request, exception):
        """
        Process the exception and return a response.

        Args:
            request: The request object.
            exception: The exception object.

        Returns:
            A response object.

        """
        self.log_exception(request, exception)
        raise exception
