from aiohttp.abc import AbstractAccessLogger

from .context import LoggingContext


class AccessLogger(AbstractAccessLogger):
    def log(self, request, response, time):
        self.logger.info(
            "Request Processed",
            **LoggingContext(request, response, time=time).for_logging()
        )
