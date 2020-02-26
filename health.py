import sys
from asyncio import get_event_loop

from aiohttp import ClientSession


async def main():
    server = sys.argv[1]
    async with ClientSession() as cs:
        try:
            async with cs.get(
                f"http://{server}/api/v1/healthz",
                headers={"X-B3-TraceID": "182f3204-09da-4851-8c22-4180734d42cf"},
            ) as res:
                if res.status < 400:
                    sys.exit(0)
                sys.exit(2)
        except ConnectionRefusedError:
            sys.exit(2)


if __name__ == "__main__":
    loop = get_event_loop()
    loop.run_until_complete(main())
