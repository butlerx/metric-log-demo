import gc
from asyncio import AbstractEventLoop, all_tasks
from typing import Dict

from prometheus_client.core import REGISTRY, CounterMetricFamily, GaugeMetricFamily


class AsyncTaskCollector:
    loops: Dict[str, AbstractEventLoop] = {}

    @staticmethod
    def track_loop(name: str, loop: AbstractEventLoop):
        AsyncTaskCollector.loops[name] = loop

    def collect(self):
        active_tasks = GaugeMetricFamily(
            "python_asyncio_active_tasks_count",
            "The number of Python Async tasks which are within a certain state",
            labels=["state", "loop"],
        )

        for name, loop in AsyncTaskCollector.loops.items():
            tasks = all_tasks(loop=loop)
            active_tasks.add_metric(
                ["running", name], sum(1 for task in tasks if not task.done())
            )
            active_tasks.add_metric(
                ["complete", name], sum(1 for task in tasks if task.done())
            )
            active_tasks.add_metric(
                ["success", name],
                sum(1 for task in tasks if task.done() and not task.exception()),
            )
            active_tasks.add_metric(
                ["failed", name],
                sum(1 for task in tasks if task.done() and task.exception()),
            )

        yield active_tasks


class GCStatsCollector:
    def collect(self):
        objects = GaugeMetricFamily(
            "python_gc_objects_count",
            "The number of objects within a Python garbage collector generation",
            labels=["generation"],
        )
        for gen, count in enumerate(gc.get_count()):
            objects.add_metric([f"{gen}"], count)
        yield objects

        collections = CounterMetricFamily(
            "python_gc_collections_count",
            "The number of times a specific garbage collector generation has been collected",
            labels=["generation"],
        )

        collected = CounterMetricFamily(
            "python_gc_collected_count",
            "The number of objects collected within a garbage collector generation",
            labels=["generation"],
        )

        uncollectable = CounterMetricFamily(
            "python_gc_collected_count",
            "The number of objects collected within a garbage collector generation",
            labels=["generation"],
        )

        for gen, stats in enumerate(gc.get_stats()):
            collections.add_metric([f"{gen}"], stats["collections"])
            collected.add_metric([f"{gen}"], stats["collected"])
            uncollectable.add_metric([f"{gen}"], stats["uncollectable"])

        yield collections
        yield collected
        yield uncollectable
