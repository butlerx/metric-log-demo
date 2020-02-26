from sys import exc_info
from traceback import format_exc
from typing import Any, Dict, Union
from uuid import uuid4

from aiohttp.web import Request, Response


class LoggingContext:
    def __init__(
        self,
        request: Request = None,
        body: str = None,
        response: Response = None,
        time: float = None,
    ):
        self.db: Dict[str, Any] = {}
        self.trace = (
            dict(id=request.headers.get("X-B3-TraceID"))
            if request and "X-B3-TraceID" in request.headers
            else dict(id=str(uuid4()))
        )
        self.http = dict(
            request=dict(
                method=request.method, url=str(request.url), body=body if body else ""
            )
            if request
            else dict(body=body if body else ""),
            response=dict(status_code=response.status) if response else dict(),
            version=f"{request.version.major}.{request.version.minor}"
            if request
            else None,
        )
        if time:
            self.request = dict(time=time)

        if request:
            self.url = dict(
                path=request.path,
                domain=request.host,
                query=request.query_string,
                scheme=request.scheme,
            )
            self.source = dict(address=request.remote, ip=request.remote)
        else:
            self.url = {}
            self.source = {}
        self.error: Dict[str, str] = {}
        self.service: Dict[str, Union[str, dict]] = {}

    def for_logging(self) -> dict:
        return {
            key: self._clean(value)
            for key, value in self.__dict__.items()
            if len(value)
        }

    def _clean(self, data):
        new_data = {}
        for k, v in data.items():
            if isinstance(v, dict):
                v = self._clean(v)
            if v not in ("", None, {}):
                new_data[k] = v
        return new_data

    def capture_error(self):
        exi = exc_info()
        if exi is not None:
            self.error = dict(msg=str(exi[1]), stack_trace=format_exc())
