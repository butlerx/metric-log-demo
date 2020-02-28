import datetime
import sys
import uuid
from argparse import ArgumentParser
from asyncio import get_event_loop

from aiohttp import ClientSession

now = datetime.datetime.now()


async def main(server: str, data: dict):
    async with ClientSession() as cs:
        try:
            async with cs.post(
                f"http://{server}/api/v1/beers",
                headers={"X-B3-TraceID": str(uuid.uuid4())},
                json=data,
            ) as resp:
                if resp.status < 400:
                    print(await resp.json())
                    sys.exit(0)
                print(resp.status, await resp.text())
                sys.exit(2)
        except ConnectionRefusedError:
            print("unable to connect")
            sys.exit(2)


def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--server", type=str, default="localhost:5000", help="server host:port"
    )
    parser.add_argument("name", type=str, help="Name of Beer", default="JudgeJuicy")
    parser.add_argument("brewery", type=str, help="Name of Brewery", default="Rascals")
    parser.add_argument(
        "--year", type=int, default=now.year, help="year beer was brewed"
    )
    parser.add_argument("--abv", type=int, default=6, help="ABV of beer")
    parser.add_argument("--size", type=int, default=440, help="Size of beer purchased")
    parser.add_argument("--purchased", type=int, help="Number of beers purchased")
    parser.add_argument(
        "--style", type=str, help="Style of beer", default="New England IPA"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    loop = get_event_loop()
    loop.run_until_complete(
        main(
            args.server,
            data=dict(
                name=args.name,
                brewery=args.brewery,
                year=args.year,
                abv=args.abv,
                style=args.style,
                size=args.size,
                drunk=False,
                stock=args.purchased,
                purchased=args.purchased,
            ),
        )
    )
