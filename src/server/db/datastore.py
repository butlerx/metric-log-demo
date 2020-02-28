from typing import List

from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily
from structlog import get_logger

from ..logging import LoggingContext
from .inventory import INVENTORY
from .metrics import purchased_by_labels, stock_by_labels


class Inventory(object):
    """
    Repository object providing access to the Iventory
    """

    def __init__(self):
        self._store = INVENTORY
        self.logger = get_logger("Inventory")

    @staticmethod
    def match_info(info: dict, query: dict) -> bool:
        """
        Determines whether a given info matches the provided query
        """
        if not (len(info) and len(query)):
            return True

        return any(
            [True for key in query.keys() if key in info and info[key] == query[key]]
        )

    async def list(self, query={}, trace: LoggingContext = None) -> List[dict]:
        trace = trace or LoggingContext()
        trace.db.update(query=query)
        self.logger.info("retrieving list of beers", **trace.for_logging())

        if not query or len(query) == 0:
            return self._store

        return list([beer for beer in self._store if self.match_info(beer, query)])

    async def store(self, beer: dict, trace={}) -> dict:
        trace = trace or LoggingContext()
        trace.db.update(payload=beer, id=id)
        self.logger.info("adding entry to db", **trace.for_logging())
        ev = {}
        ev.update(beer)
        self._store.append(ev)
        self.logger.debug("added entry to db", **trace.for_logging())
        return ev

    async def get(self, id: int, trace={}):
        trace = trace or LoggingContext()
        trace.db.update(id=id)
        self.logger.debug("fetching beer from db", **trace.for_logging())
        return self._store[id]

    async def update(self, id: str, beer: dict, trace={}) -> dict:
        trace = trace or LoggingContext()
        trace.db.update(id=id, payload=beer)
        if id not in self._store:
            self.logger.info("beer not found in db", **trace.for_logging())
            return {}
        ev = {}
        ev.update(beer)
        self._store[id] = ev
        self.logger.info("beer updated in db", **trace.for_logging())
        return ev

    async def remove(self, id: str, trace={}) -> bool:
        trace = trace or LoggingContext()
        trace.db.update(id=id)
        self.logger.info("deleting beer from db", **trace.for_logging())
        if id in self._store:
            del self._store[id]
            self.logger.info("beer deleted from db", **trace.for_logging())
            return True
        self.logger.info("beer failed to delete, no beer found", **trace.for_logging())
        return False

    async def clear(self, trace: LoggingContext = None):
        trace = trace or LoggingContext()
        self.logger.info("clearing db", **trace.for_logging())
        self._store = []
        self.logger.warn("db deleted", **trace.for_logging())
        return True

    async def instock(self, query={}, trace: LoggingContext = None) -> List[dict]:
        """
        Retrieves the list of active beer present in this datastore
        """
        trace = trace or LoggingContext()
        trace.db.update(query=query)
        self.logger.debug("getting list of active beer", **trace.for_logging())
        return [
            beer
            for beer in self._store
            if beer["stock"] > 0 and self.match_info(beer, query)
        ]

    def collect(self):
        """
        Collects metrics describing the state of this store
        """
        labels = ["brewery", "style", "abv"]
        beer_purchased = CounterMetricFamily(
            "beer_purchased", "The number of beers purchased", labels=labels,
        )

        beer_stock = GaugeMetricFamily(
            "beer_stock", "The number of beers in stock", labels=labels,
        )

        purchased = purchased_by_labels(labels, self._store)
        stock = stock_by_labels(labels, self._store)

        for labels, count in purchased:
            beer_purchased.add_metric(labels, count)

        for labels, count in stock:
            beer_stock.add_metric(labels, count)

        yield beer_purchased
        yield beer_stock
