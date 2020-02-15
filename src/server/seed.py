import random
from datetime import datetime, timedelta
from uuid import uuid4


def seed_events() -> dict:
    return {
        event["id"]: event
        for event in [
            {
                "id": uuid4().hex,
                "title": f"event_{num}",
                "fromDate": f"{rand_date()}Z",
                "untilDate": f"{rand_date()}Z",
            }
            for num in range(100)
        ]
    }


def rand_date():
    random.seed(datetime.now())
    start = datetime(2020, 1, 1)
    return (
        start + timedelta(days=random.randint(1, (datetime(2020, 12, 1) - start).days))
    ).isoformat()
