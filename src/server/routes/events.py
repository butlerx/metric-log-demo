"""
events API
"""
from json import JSONDecodeError

from aiohttp import web
from prometheus_async.aio import time

from ..logging import LoggingContext
from .base import REQ_TIME, APIBase


class EventsAPI(APIBase):
    def add_routes(self):
        self.router.add_get("", self.list)
        self.router.add_get("/active", self.active)
        self.router.add_post("", self.add)

    @time(REQ_TIME.labels("GET", "/api/v1/events"))
    async def list(self, request: web.Request):
        """
        GET /api/v1/events?query...
        Retrieves the list of events which match a given query
        from the datastore.
        """
        trace = LoggingContext(request=request)
        events = await self.store.list(request.query, trace=trace)
        return web.json_response(events)

    @time(REQ_TIME.labels("GET", "/api/v1/events/active"))
    async def active(self, request: web.Request):
        """
        GET /api/v1/events/active?query...
        Retrieves the list of active events which match a given query
        from the datastore.
        """
        trace = LoggingContext(request=request)
        events = await self.store.active(dict(request.query), trace=trace)
        return web.json_response(events)

    @time(REQ_TIME.labels("POST", "/api/v1/events"))
    async def add(self, request: web.Request):
        """
        POST /api/v1/events
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
            return await self.JSONError("/api/v1/events", trace=trace)
