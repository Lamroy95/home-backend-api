from typing import List, Optional, Union

from pydantic import BaseModel, validator


class Fan(BaseModel):
    mode: str
    motor_speed: int
    filter_days_left: int
    manual_fan_level: int


class SensorValue(BaseModel):
    value: Union[int, float, str]
    timestamp: int


class Sensor(BaseModel):
    id: str
    name: str
    unit: Optional[str] = ""
    max: Optional[int] = None
    min: Optional[int] = None
    normal: Optional[int] = None
    gauge: bool
    values: Optional[List[SensorValue]] = None


class Room(BaseModel):
    name: str
    sensors: List[Sensor]
    fan: Optional[Fan]


class Place(BaseModel):
    name: str
    rooms: List[Room]
