from functools import wraps
from typing import Any, Callable

from flask import current_app

from application.db.models import MetricSnapshot


def app_route(*args: str, **kwargs: Any) -> Callable:  # noqa: ANN401
    def decorator(func: Callable) -> Callable:
        func.routes = args  # type: ignore[attr-defined]
        func.kwargs = kwargs  # type: ignore[attr-defined]

        @wraps(func)
        def wrapper(self: Any) -> str:  # noqa: ANN401
            current_app.logger.info("Route accessed: %s", args)

            return func(self)

        return wrapper

    return decorator


def print_snapshots(snapshots: list[MetricSnapshot]) -> None:
    print("\n\033[1;92m============================\033[0;0m\n")

    for snapshot in snapshots:
        print("Snapshot:")
        print(f"    ID:      {snapshot.id}")
        print(f"    DEVICE:  {snapshot.device}")
        print(f"    TIME:    {snapshot.timestamp}")
        print("    METRICS:")

        for metric in snapshot.metrics:
            print(f"        {metric}")

    print("\n\033[1;92m============================\033[0;0m\n")
