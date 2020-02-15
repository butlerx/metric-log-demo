"""
events API
"""
from json import JSONDecodeError
from typing import Any, Dict

from aiohttp import web
from prometheus_async.aio import time

from ..logging import LoggingContext
from .base import REQ_TIME, APIBase
from .error import api_error


class EventAPI(APIBase):
    def add_routes(self):
        self.router.add_get("/{id}", self.get)
        self.router.add_patch("/{id}", self.patch)
        self.router.add_delete("/{id}", self.delete)

    @time(REQ_TIME.labels("GET", "/api/v1/event/:id"))
    async def get(self, request: web.Request):
        """
        GET /api/v1/event/{id}

        Retrieves a specific event entry from the store.
        """
        trace = LoggingContext(request=request)
        entry = await self.store.get(request.match_info.get("id"), trace=trace)
        return web.json_response(entry) if entry else await self.notFound()

    @time(REQ_TIME.labels("PATCH", "/api/v1/event/:id"))
    async def patch(self, request: web.Request):
        """
        PATCH /api/v1/event/{id}

        Updates the provided fields of the event entry from the store.
        """
        trace = LoggingContext(request=request)
        id = request.match_info.get("id")
        trace.update(id=id)
        entry = await self.store.get(id, trace=trace)
        if not entry:
            return await self.notFound()

        try:
            patch = await request.json()
            trace.update(patch=patch)
            event: Dict[str, Any] = {}
            event.update(patch)
            event.update({"id": id})  # Make sure we don't overwrite the ID
            trace.update(event=event)
            event = await self.store.update(id, event, trace=trace)
            return web.json_response(event)
        except JSONDecodeError:
            return await self.JSONError(f"/api/v1/event/{id}", trace)

    @time(REQ_TIME.labels("DELETE", "/api/v1/event/:id"))
    async def delete(self, request: web.Request):
        """
        DELETE /api/v1/event/{id}

        Removes a specific event entry from the store.
        """
        trace = LoggingContext(request=request)
        id = request.match_info.get("id")
        trace.update(id=id)
        entry = await self.store.get(id, trace=trace)
        if not entry:
            return await self.notFound()

        removed = await self.store.remove(id, trace=trace)
        if not removed:
            self.logger.error(
                "We found the entry you requested, but were unable to remove it.",
                **trace.for_logging(),
            )
            return await api_error(
                500,
                "Server Error",
                "We found the entry you requested, but were unable to remove it. Please try again later.",
            )

        return web.Response(status=200)
