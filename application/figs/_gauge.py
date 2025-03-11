from pydantic import BaseModel


class Gauge(BaseModel):
    device: str
    value: float
    label: str
