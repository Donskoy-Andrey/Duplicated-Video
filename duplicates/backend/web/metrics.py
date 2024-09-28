import time
from typing import Callable, Awaitable

from prometheus_client import (
    Counter,
    Histogram,
)
from prometheus_client.utils import INF
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match, Route
from starlette.types import Scope


_DEFAULT_BUCKETS = (
    0.1,
    0.2,
    0.5,
    0.8,
    1,
    INF,
)


REQUESTS_TOTAL = Counter(
    'requests_total',
    'Total count of responses by method and path_template.',
    ('method', 'path_template'),
)

REQUESTS_PROCESSING_TIME = Histogram(
    'requests_processing_time',
    'Histogram of requests processing time by path_template (in seconds)',
    ('method', 'path_template'),
    buckets=_DEFAULT_BUCKETS,
)

EXCEPTIONS_TOTAL = Counter(
    'exceptions_total',
    'Total count of exceptions raised by path_template and exception type',
    ('method', 'path_template'),
)


async def http_prometheus_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
    exclude_routes: set[str] | None = None,
) -> Response:
    if exclude_routes is not None:
        for exclude_route in exclude_routes:
            if request.url.path.startswith(exclude_route):
                return await call_next(request)

    path_template = _get_path_template(request.scope)

    REQUESTS_TOTAL.labels(method=request.method, path_template=path_template).inc()
    before_time = time.perf_counter()
    try:
        response = await call_next(request)
    except BaseException as e:
        EXCEPTIONS_TOTAL.labels(
            method=request.method,
            path_template=path_template,
        ).inc()
        raise e from None
    else:
        after_time = time.perf_counter()
        REQUESTS_PROCESSING_TIME.labels(
            method=request.method,
            path_template=path_template,
        ).observe(
            after_time - before_time,
        )

    return response


def _get_path_template(scope: Scope) -> str:
    route: Route
    for route in scope['app'].routes:
        match, child_scope = route.matches(scope)
        if match == Match.FULL:
            return route.path

    return 'unknown'
