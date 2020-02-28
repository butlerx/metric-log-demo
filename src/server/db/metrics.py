from typing import Callable, Dict, List, Tuple


def field_by_labels(field: str) -> Callable:
    def _func(labels: List[str], beers) -> List[Tuple[List[str], int]]:
        res: Dict[str, int] = {}
        for beer in beers:
            label = "__".join([str(beer[l]) for l in labels])
            res[label] = beer[field] + (res[label] if label in res else 0)
        return [(key.split("__"), value) for key, value in res.items()]

    return _func


purchased_by_labels = field_by_labels("purchased",)
stock_by_labels = field_by_labels("stock")
