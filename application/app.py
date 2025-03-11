from datetime import datetime as dt
from json import loads
from typing import TYPE_CHECKING, Any

from cotc_common.types import JSONArr, ServerResponse
from flask import render_template, request
from requests import status_codes
from sqlalchemy.exc import OperationalError

from application.base import AppBase
from application.common import app_route
from application.figs import Gauge

if TYPE_CHECKING:
    from application.db.models import MetricSnapshot


class App(AppBase):
    last_update: dt

    def __init__(self) -> None:
        super().__init__(__name__)
        self.last_update = dt.now()

    @app_route("/", "/latest")
    def route_latest(self) -> str:
        try:
            gauge: Gauge | None = None
            with self.db:
                snapshots: list[MetricSnapshot] = self.db.get_snapshots(2, desc=True)
                for s in snapshots:
                    for m in s.metrics:
                        if m.unit == "%":
                            gauge = Gauge(
                                device=s.device.name, value=m.value, label=m.name
                            )
                            break
                    else:
                        continue
                    break
                return render_template("latest.html", snapshots=snapshots, gauge=gauge)
        except OperationalError:
            self.logger.exception("Error getting snapshots from database")
            return render_template("latest.html", snapshots=[], gauge=None)

    @app_route("/all", "/history")
    def route_history(self) -> str:
        try:
            with self.db:
                snapshots: list[MetricSnapshot] = self.db.get_snapshots(desc=True)
                return render_template("history.html", snapshots=snapshots)
        except OperationalError:
            self.logger.exception("Error getting snapshots from database")
            return render_template("history.html", snapshots=[])

    @app_route("/metrics", methods=["POST"])
    def route_json(self) -> ServerResponse:
        data_list: Any = request.json
        json: JSONArr | Any = loads(data_list)

        self.logger.info("JSON data received")

        if not isinstance(json, list):
            return {"error": "Invalid JSON data"}, 400

        for snapshot in json:
            ret: ServerResponse = self.db.add_snapshot(snapshot)
            if ret[1] != status_codes.codes.ok:
                return ret

        self.last_update = dt.now()

        return ret

    @app_route("/check_update")
    def route_check_update(self) -> ServerResponse:
        return {"last_update": self.last_update.isoformat()}, 200

    def route_404(self, _: Exception) -> tuple[str, int]:
        return render_template("404.html"), 404
