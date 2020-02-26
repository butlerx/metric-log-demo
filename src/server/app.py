from asyncio import get_event_loop
from datetime import datetime

from aiohttp import web
from aiohttp_cors import ResourceOptions, setup
from prometheus_async.aio.web import server_stats

from .db import Inventory
from .middlewares import errors
from .routes import BeerAPI, BeersAPI
from .runtime_metrics import AsyncTaskCollector, GCStatsCollector


class Server(web.Application):
    def __init__(self, *args, **kwargs) -> None:
        web.Application.__init__(self, *args, **kwargs)

        self.cors = setup(
            self,
            defaults={
                "*": ResourceOptions(
                    allow_methods=["GET", "POST", "PATCH"],
                    allow_headers=["Content-Type"],
                )
            },
        )

        self.started = datetime.utcnow()
        self.store = Inventory()
        self.task_collector = AsyncTaskCollector()
        self.stats_collector = GCStatsCollector()
        self.task_collector.track_loop("server", get_event_loop())

        # Mount the API applications on their endpoints
        self.add_subapp(
            "/api/v1/beers", BeersAPI(self.store, *args, **kwargs),
        )
        self.add_subapp(
            "/api/v1/beer", BeerAPI(self.store, *args, **kwargs),
        )

        self.router.add_get("/metrics", server_stats)
        self.router.add_get("/api/v1/metrics", server_stats)
        self.router.add_get("/api/v1/healthz", self.health)

        for route in list(self.router.routes()):
            self.cors.add(route)

        # Register application middleware
        self.middlewares.append(errors())

    async def health(self, request: web.Request):
        """
        GET /api/v1/healthz

        A very simple healthcheck endpoint which can be used to determine
        when the service is running healthily or not.
        """
        return web.json_response({"started": self.started.isoformat()})
