import uuid
import time
import logging
from contextvars import ContextVar

logger = logging.getLogger(__name__)


class RequestFilter(logging.Filter):
    def filter(self, record):
        record.request_id = ctx_request_id.get()
        return record


ctx_request_id = ContextVar("request_id")

context_filter = RequestFilter()
logger.addFilter(context_filter)


def LoggingMiddleware(get_response):
    def middleware(request):
        # Create a request ID
        request_id = str(uuid.uuid4())

        ctx_request_id.set(request_id)

        request.start_time = time.time()

        response = get_response(request)

        elapsed = time.time() - request.start_time

        params = {
            "path": request.path,
            "method": request.method,
            "status_code": response.status_code,
            "response_size": len(response.content),
            "elapsed": elapsed,
        }

        logger.info("incoming '%s' request to '%s'", request.method, request.path)

        response["X-Request-ID"] = request_id

        return response

    return middleware
