from __future__ import annotations

import logging
import time

logger = logging.getLogger("REQUEST")


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info("%s %s", request.method, request.path)

        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        logger.info(
            "%s %s: %d in %.2f",
            request.method,
            request.path,
            response.status_code,
            duration,
        )

        return response
