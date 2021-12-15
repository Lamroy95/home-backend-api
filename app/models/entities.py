from contextlib import suppress
from enum import Enum
from typing import Union

from pydantic import BaseModel, validator, root_validator

from app.config import SENSORS_NAMES_MAP, SENSORS_VALUE_PROCESSORS


class Measurement(BaseModel):
    value: Union[int, float, str]
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
        with suppress(ValueError):
            return float(v)
        return v


class Commands(Enum):
    SET_AUTO = "set_auto"
    SET_LEVEL = "set_level"
