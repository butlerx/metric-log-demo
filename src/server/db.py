from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from dateutil.parser import parse
from prometheus_client.core import GaugeMetricFamily
from structlog import get_logger

from .logging import LoggingContext
from .seed import seed_events


class EventStore(object):
    """
    Repository object providing access to the events datastore
    """

    def __init__(self):
        self._store = seed_events()
        self.logger = get_logger("EventStore")

    @staticmethod
    def match_info(info: dict, query: dict) -> bool:
        """
        Determines whether a given info matches the provided query
        """
        if not info:
            return True

        return any(
            [True for key in query.keys() if key in info and info[key] == query[key]]
        )

    @staticmethod
    def make_id() -> str:
        """
        Generates a unique ID for an event entry.
        """
        return str(uuid4().hex)

    async def list(self, query={}, trace: LoggingContext = None) -> List[dict]:
        trace = trace or LoggingContext()
        trace.db.update(query=query)
        self.logger.info("retrieving list of events", **trace.for_logging())

        if not query or len(query) == 0:
            return list(self._store.values())

        return list(
            [
                event
                for id, event in self._store.items()
                if self.match_info(event, query)
            ]
        )

    async def store(self, event: dict, trace={}) -> dict:
        trace = trace or LoggingContext()
        id = self.make_id()
        trace.db.update(payload=event, id=id)
        self.logger.info("adding entry to db", **trace.for_logging())
        ev = {}
        ev.update(event)
        ev.update({"id": id})
        self._store[id] = ev
        self.logger.debug("added entry to db", **trace.for_logging())
        return ev

    async def get(self, id: str, trace={}):
        trace = trace or LoggingContext()
        trace.db.update(id=id)
        self.logger.debug("fetching event from db", **trace.for_logging())
        return self._store.get(id)

    async def update(self, id: str, event: dict, trace={}) -> dict:
        trace = trace or LoggingContext()
        trace.db.update(id=id, payload=event)
        if id not in self._store:
            self.logger.info("event not found in db", **trace.for_logging())
            return {}
        ev = {}
        ev.update(event)
        ev.update({"id": id})
        self._store[id] = ev
        self.logger.info("event updated in db", **trace.for_logging())
        return ev

    async def remove(self, id: str, trace={}) -> bool:
        trace = trace or LoggingContext()
        trace.db.update(id=id)
        self.logger.info("deleting event from db", **trace.for_logging())
        if id in self._store:
            del self._store[id]
            self.logger.info("event deleted from db", **trace.for_logging())
            return True
        self.logger.info(
            "event failed to delete, no event found", **trace.for_logging()
        )
        return False

    async def clear(self, trace: LoggingContext = None):
        trace = trace or LoggingContext()
        self.logger.info("clearing db", **trace.for_logging())
        self._store = {}
        self.logger.warn("db deleted", **trace.for_logging())
        return True

    async def active(self, query={}, trace: LoggingContext = None) -> List[dict]:
        """
        Retrieves the list of active event present in this datastore
        """
        trace = trace or LoggingContext()
        trace.db.update(query=query)
        now = datetime.now(timezone.utc)
        self.logger.debug("getting list of active event", **trace.for_logging())
        return [
            event
            for event in self._store.values()
            if parse(event["fromDate"]) < now < parse(event["untilDate"])
            and self.match_info(event, query)
        ]

    def collect(self):
        """
        Collects metrics describing the state of this store
        """
        c = GaugeMetricFamily(
            "db_events_count",
            "The number of events that are present in the cache",
            labels=["state"],
        )

        now = datetime.now(timezone.utc)

        c.add_metric(
            ["active"],
            len(
                [
                    event
                    for event in self._store.values()
                    if parse(event["fromDate"]) < now < parse(event["untilDate"])
                ]
            ),
        )

        c.add_metric(
            ["completed"],
            len(
                [
                    event
                    for event in self._store.values()
                    if parse(event["untilDate"]) <= now
                ]
            ),
        )

        c.add_metric(
            ["scheduled"],
            len(
                [
                    event
                    for event in self._store.values()
                    if parse(event["fromDate"]) >= now
                ]
            ),
        )

        yield c
