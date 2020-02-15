import uuid

import requests

data = {
    "fromDate": "2020-02-14T15:20:24",
    "title": "sistem 2020",
    "untilDate": "2020-02-15T15:20:24",
}
headers = {"X-B3-TraceID": str(uuid.uuid4())}
resp = requests.post("http://localhost:8000/api/v1/events", headers=headers, json=data)
resp.raise_for_status()
result = resp.json()
print(resp.text)
