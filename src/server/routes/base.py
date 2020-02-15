from aiohttp import web
from prometheus_client import Histogram
from structlog import get_logger

from ..logging import LoggingContext
from .error import api_error

REQ_TIME = Histogram(
    "req_time_seconds",
    "Time spent processing requests",
    buckets=(0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, float("inf")),
    labelnames=["method", "endpoint"],
)


class APIBase(web.Application):
    def __init__(self, store, *args, **kwargs,) -> None:
        web.Application.__init__(self, *args, **kwargs)
        self.store = store
        self.logger = get_logger()
        self.add_routes()

    def add_routes(self):
        pass

    async def JSONError(self, path: str, trace: LoggingContext):
        self.logger.error("Error Decoding JSON", **trace.for_logging())
        return await api_error(
            400,
            "Bad Request",
            "You did not provide a valid JSON object in your request",
        )

    @staticmethod
    async def notFound():
        return await api_error(
            404, "Not Found", "We could not find the maintenance entry you requested."
        )
