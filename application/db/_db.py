from __future__ import annotations

from datetime import datetime as dt
from typing import TYPE_CHECKING

from cotc_common.metrics import (
    DeviceSchema,
    MetricSchema,
    MetricSnapshotSchema,
    parse_snapshot_json,
)
from cotc_common.types import ServerResponse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc as sa_desc
from sqlalchemy.exc import OperationalError

from application.db.models import Base, Device, Metric, MetricSnapshot

if TYPE_CHECKING:
    from types import TracebackType

    from cotc_common.metrics import MetricSnapshotJson
    from cotc_common.types import JSONObj
    from flask.ctx import AppContext

    from application.base import AppBase


class DB(SQLAlchemy):
    app: AppBase
    context: AppContext | None

    def __init__(self, app: AppBase) -> None:
        super().__init__(app.web_app)
        self.app = app
        self.context = None

        with self:
            Base.metadata.bind = self.engine
            Base.query = self.session.query_property()
            Base.metadata.create_all(self.engine)
            self.app.logger.info("Database initialized")

    def __enter__(self) -> AppContext:
        self.context = self.app.web_app.app_context()
        return self.context.__enter__()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.context is not None:
            self.context.__exit__(exc_type, exc_val, exc_tb)
        self.context = None

    def add_snapshot(self, json_obj: JSONObj) -> ServerResponse:
        snapshot_json: MetricSnapshotJson | None = parse_snapshot_json(json_obj)

        if snapshot_json is None:
            self.app.logger.error("Error parsing JSON data: Invalid JSON format")
            return {"status": "error", "message": "Invalid JSON data"}, 400

        device: Device | None = None
        snapshot_schema: MetricSnapshotSchema = MetricSnapshotSchema(
            device_id=0,
            timestamp=dt.fromisoformat(snapshot_json.timestamp),
            metrics=[],
        )

        try:
            with self:
                device = (
                    self.session.query(Device)
                    .filter_by(name=snapshot_json.device.name)
                    .first()
                )
                if device is not None:
                    snapshot_schema.device_id = int(device.id)

            if device is None:
                device_name: str = snapshot_json.device.name
                device_schema: DeviceSchema = DeviceSchema(name=device_name)
                device = Device.from_json(device_schema)
                with self:
                    self._addncommit(device)
                    snapshot_schema.device_id = int(device.id)

            snapshot: MetricSnapshot = MetricSnapshot.from_json(snapshot_schema)

            with self:
                self._addncommit(snapshot)
                for metric_data in snapshot_json.metrics:
                    metric_type: MetricSchema = MetricSchema(
                        name=metric_data.name,
                        value=metric_data.value,
                        unit=metric_data.unit,
                        snapshot_id=int(snapshot.id),
                    )
                    metric: Metric = Metric.from_json(metric_type)
                    self._addncommit(metric)

                self.app.logger.info("JSON data saved to database: %s", repr(snapshot))

        except OperationalError:
            self.app.logger.exception("Error saving JSON data to database")
            return {
                "status": "error",
                "message": "Error saving JSON data to database",
            }, 500

        return {"status": "success"}, 200

    def get_snapshots(
        self,
        n: int | None = None,
        *,
        desc: bool = False,
    ) -> list[MetricSnapshot]:
        return (
            self.session.query(MetricSnapshot)
            .order_by(sa_desc(MetricSnapshot.id) if desc else MetricSnapshot.id)
            .limit(n)
            .all()
        )

    def _addncommit(self, data: Metric | MetricSnapshot | Device) -> None:
        self.session.add(data)
        self.session.commit()

    def get_filtered_snapshots(
        self,
        device_id: int | None = None,
        start_time: dt | None = None,
        end_time: dt | None = None,
        n: int | None = None,
        *,
        desc: bool = False,
    ) -> list[MetricSnapshot]:
        """
        Get snapshots filtered by device ID and/or time range

        Args:
            device_id (int | None): Optional device ID to filter by
            start_time (dt | None): Optional start time to filter by
            end_time (dt | None): Optional end time to filter by
            desc (bool): Sort in descending order (by timestamp)

        Returns:
            list[MetricSnapshot]: List of filtered MetricSnapshot objects
        """

        query = self.session.query(MetricSnapshot)

        if device_id:
            query = query.filter(MetricSnapshot.device_id == device_id)

        if start_time:
            query = query.filter(MetricSnapshot.timestamp >= start_time)

        if end_time:
            query = query.filter(MetricSnapshot.timestamp <= end_time)

        query = query.order_by(
            sa_desc(MetricSnapshot.timestamp) if desc else MetricSnapshot.timestamp
        )

        return query.limit(n).all()

    def get_devices(self, *, desc: bool = False) -> list[Device]:
        """
        Get all devices from the database

        Returns:
            List of Device objects
        """

        return (
            self.session.query(Device)
            .order_by(sa_desc(Device.name) if desc else Device.name)
            .all()
        )
