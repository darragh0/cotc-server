from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cotc_common.util import utc_now
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from cotc_common.metrics import DeviceSchema, MetricSchema, MetricSnapshotSchema

Base: Any = declarative_base()


class Device(Base):
    __tablename__ = "device"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    snapshots = relationship(
        "MetricSnapshot",
        backref="device",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Device[Name={self.name!r}]"

    @staticmethod
    def from_json(data: DeviceSchema) -> Device:
        return Device(name=data.name)


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshot"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("device.id"), nullable=False)
    timestamp = Column(DateTime, default=utc_now)
    metrics = relationship(
        "Metric",
        backref="snapshot",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"MetricSnapshot[Device={self.device!r}, Time={self.timestamp!r}]"

    @staticmethod
    def from_json(data: MetricSnapshotSchema) -> MetricSnapshot:
        return MetricSnapshot(
            device_id=data.device_id,
            timestamp=data.timestamp,
        )


class Metric(Base):
    __tablename__ = "metric"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    snapshot_id = Column(
        Integer,
        ForeignKey("metric_snapshot.id"),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"Metric[Name={self.name!r}, Data='{self.value}{self.unit}']"

    @staticmethod
    def from_json(data: MetricSchema) -> Metric:
        return Metric(
            name=data.name,
            value=data.value,
            unit=data.unit,
            snapshot_id=data.snapshot_id,
        )
