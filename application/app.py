from datetime import datetime as dt
from json import loads
from typing import TYPE_CHECKING, Any

from cotc_common.types import JSONArr, ServerResponse
from flask import render_template, request
from requests import status_codes
from sqlalchemy.exc import OperationalError

from application.base import AppBase
from application.common import app_route, validate_int, validate_time
from application.figs import Gauge

if TYPE_CHECKING:
    from application.db.models import Device, MetricSnapshot


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
            start_time: dt | None = validate_time(request.args.get("start_time", ""))
            end_time: dt | None = validate_time(request.args.get("end_time", ""))
            device_id: int | None = validate_int(request.args.get("device", ""))

            snapshots: list[MetricSnapshot]
            with self.db:
                devices: list[Device] = self.db.get_devices()

                if (
                    device_id is not None
                    or start_time is not None
                    or end_time is not None
                ):
                    snapshots = self.db.get_filtered_snapshots(
                        device_id=device_id,
                        start_time=start_time,
                        end_time=end_time,
                        desc=True,
                    )
                else:
                    snapshots = self.db.get_snapshots(desc=True)

                return render_template(
                    "history.html",
                    snapshots=snapshots,
                    devices=devices,
                    selected_device=device_id,
                    start_time=start_time,
                    end_time=end_time,
                )
        except OperationalError:
            self.logger.exception("Error getting snapshots from database")
            return render_template("history.html", snapshots=[], devices=[])

    @app_route("/metrics", methods=["POST"])
    def route_json(self) -> ServerResponse:
        data_list: Any = request.json
        json: JSONArr | Any = loads(data_list)

        self.logger.info("JSON data received")

        if not isinstance(json, list):
            return {"error": "Invalid JSON data"}, 400

        resp: ServerResponse = {"status": "ok"}, 200
        for snapshot in json:
            ret = self.db.add_snapshot(snapshot)
            if ret[1] != status_codes.codes.ok:
                return ret
            device_name, rank = ret[0].popitem()
            resp[0][device_name] = rank

        self.last_update = dt.now()
        return resp

    @app_route("/check_update")
    def route_check_update(self) -> ServerResponse:
        return {"last_update": self.last_update.isoformat()}, 200

    def route_404(self, _: Exception) -> tuple[str, int]:
        return render_template("404.html"), 404
