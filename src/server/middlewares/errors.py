from typing import Callable

from aiohttp import ClientResponse
from aiohttp.web import HTTPException, Request, RequestHandler, middleware
from structlog import get_logger

from ..logging import LoggingContext
from ..routes import api_error


def errors() -> Callable:
    """
    Error handler middleware which provides routing of HTTP errors
    to the correct error handlers.

    """
    logger = get_logger("middleware.errors")

    @middleware
    async def middleware_handler(request: Request, handler: RequestHandler):
        trace = LoggingContext(request=request, body=await request.text())
        try:
            response: ClientResponse = await handler(request)
            if response.status >= 400:
                return await api_error(response.status)
            return response
        except HTTPException as httpEx:
            trace.http.update(response={"status": httpEx.status, "body": httpEx.body})
            trace.capture_error()
            logger.error("error handling web request", **trace.for_logging())
            return await api_error(httpEx.status)
        except Exception:
            trace.http.update(response={"status": 500})
            trace.capture_error()
            logger.error("error handling web request", **trace.for_logging())
            return await api_error(500)

    return middleware_handler
