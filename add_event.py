import sys
import uuid
from asyncio import get_event_loop

from aiohttp import ClientSession

data = {
    "fromDate": "2020-02-29T09:00:00Z",
    "title": "sistem 2020",
    "untilDate": "2020-02-29T17:00:00Z",
}
headers = {"X-B3-TraceID": str(uuid.uuid4())}


async def main():
    server = sys.argv[1]
    async with ClientSession() as cs:
        try:
            async with cs.post(
                f"http://{server}/api/v1/events", headers=headers, json=data
            ) as resp:
                if resp.status < 400:
                    print(await resp.json())
                    sys.exit(0)
                print(resp.status, await resp.text())
                sys.exit(2)
        except ConnectionRefusedError:
            print("unable to connect")
            sys.exit(2)


if __name__ == "__main__":
    loop = get_event_loop()
    loop.run_until_complete(main())
