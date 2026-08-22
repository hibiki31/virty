from fastapi.routing import iter_route_contexts
from prometheus_fastapi_instrumentator import routing
from starlette.requests import Request
from starlette.routing import Match, Route


def get_route_name(request: Request) -> str | None:
    """FastAPIのinclude contextを展開し、低cardinalityなroute名を返す。"""

    partial_route_name: str | None = None
    for route_context in iter_route_contexts(request.app.routes):
        if isinstance(route_context, Route):
            match, _ = Route.matches(route_context, request.scope)
        else:
            match, _ = route_context.matches(request.scope)

        path = getattr(route_context, "path", None)
        route_name = path if isinstance(path, str) else None
        if match == Match.FULL:
            return route_name or request.scope.get("path")
        if match == Match.PARTIAL:
            partial_route_name = route_name

    return partial_route_name


def install_prometheus_route_compatibility() -> None:
    """Instrumentator 7系へFastAPI 0.137以降のroute解決を適用する。"""

    setattr(routing, "get_route_name", get_route_name)
