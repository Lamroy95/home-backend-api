from contextlib import suppress
from typing import List, Optional, Union

from pydantic import BaseModel, validator, root_validator

from app.config import SENSORS_NAMES_MAP, SENSORS_VALUE_PROCESSORS


class Sensor(BaseModel):
    id: str
    name: str
    unit: str
    max: Optional[Union[float, int]] = None
    min: Optional[Union[float, int]] = None


class Room(BaseModel):
    name: str
    sensors: List[Sensor]


class Place(BaseModel):
    name: str
    rooms: List[Room]


class Measurement(BaseModel):
    value: float
    name: str
    place: str
    room: str

    @root_validator
    def normalize_values(cls, values: dict):
        name, val = values.get("name"), values.get("value")
        if func := SENSORS_VALUE_PROCESSORS.get(name):
            values["value"] = func(val)
        return values

    @validator("name")
    def rename_sensors(cls, name):
        return SENSORS_NAMES_MAP.get(name, name)

    @validator("value")
    def parse_str_value(cls, v):
        with suppress(ValueError):
            return int(v)
        return float(v)
