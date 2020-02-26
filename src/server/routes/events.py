"""
Beers API
"""
from json import JSONDecodeError

from aiohttp import web
from prometheus_async.aio import time

from ..logging import LoggingContext
from .base import REQ_TIME, APIBase


class BeersAPI(APIBase):
    def add_routes(self):
        self.router.add_get("", self.list)
        self.router.add_get("/instock", self.instock)
        self.router.add_post("", self.add)

    @time(REQ_TIME.labels("GET", "/api/v1/beers"))
    async def list(self, request: web.Request):
        """
        GET /api/v1/beers?query...
        Retrieves the list of beers which match a given query
        from the datastore.
        """
        trace = LoggingContext(request=request)
        beers = await self.store.list(request.query, trace=trace)
        return web.json_response(beers)

    @time(REQ_TIME.labels("GET", "/api/v1/beers/instock"))
    async def instock(self, request: web.Request):
        """
        GET /api/v1/beers/instock?query...
        Retrieves the list of instock beers which match a given query
        from the datastore.
        """
        trace = LoggingContext(request=request)
        beers = await self.store.instock(dict(request.query), trace=trace)
        return web.json_response(beers)

    @time(REQ_TIME.labels("POST", "/api/v1/beers"))
    async def add(self, request: web.Request):
        """
        POST /api/v1/beers
        Stores a new event entry in the datastore and returns
        the final object.
        """
        trace = LoggingContext(request=request)

        if not request.body_exists:
            self.logger.info("request body empty", **trace.for_logging())
            return web.HTTPBadRequest()
        try:
            payload = await request.json()
            trace.http["request"].update(body=payload)
            event = await self.store.store(payload, trace=trace)
            return web.json_response(event)
        except JSONDecodeError:
            return await self.JSONError("/api/v1/beers", trace=trace)
