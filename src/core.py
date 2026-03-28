import os
from pathlib import Path
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, field_validator, EmailStr
from datetime import datetime
from strictyaml import load


PACKAGE_ROOT = Path().resolve()
ASSETS_PATH =  PACKAGE_ROOT / "assets"
CONFIG_FILE_PATH = ASSETS_PATH / "config.yml"


class DataSchema(BaseModel):
    """
    Schema for raw data and model data
    """

    columns_to_keep: List[str]
    date_columns: List[str]
    int_columns: List[str]
    float_columns: List[str]
    normalize_phone: bool = True


class Config(BaseModel):
    """Master config object."""

    data_config: DataSchema


class Name(BaseModel):
    title: Optional[str]
    first: Optional[str]
    last: Optional[str]


class Street(BaseModel):
    number: Optional[int]
    name: Optional[str]


class Coordinates(BaseModel):
    latitude: Optional[float]
    longitude: Optional[float]


class Timezone(BaseModel):
    offset: Optional[str]
    description: Optional[str]


class Location(BaseModel):
    street: Optional[Street]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postcode: Optional[Union[int, str]]
    coordinates: Optional[Coordinates]
    timezone: Optional[Timezone]


class Login(BaseModel):
    uuid: Optional[str]
    username: Optional[str]
    password: Optional[str]
    salt: Optional[str]
    md5: Optional[str]
    sha1: Optional[str]
    sha256: Optional[str]


class Dob(BaseModel):
    date: Optional[datetime]
    age: Optional[int]


class Registered(BaseModel):
    date: Optional[datetime]
    age: Optional[int]


class Id(BaseModel):
    name: Optional[str]
    value: Optional[str]


class Picture(BaseModel):
    large: Optional[str]
    medium: Optional[str]
    thumbnail: Optional[str]

class RawDataSchema(BaseModel):
    gender: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    cell: Optional[str]
    nat: Optional[str]

    name: Optional[Name]
    location: Optional[Location]
    login: Optional[Login]
    dob: Optional[Dob]
    registered: Optional[Registered]
    id: Optional[Id]
    picture: Optional[Picture]

    # -------------------------
    # Validações úteis
    # -------------------------

    @field_validator("phone", "cell", mode="before")
    def clean_phone(cls, v):
        if v:
            return v.replace(" ", "").replace("-", "")
        return v

    @field_validator("gender")
    def validate_gender(cls, v):
        if v and v not in {"male", "female"}:
            raise ValueError("Invalid gender")
        return v

class MultipleDataSchema(BaseModel):
    '''Master model validation object'''
    inputs_raw: List[RawDataSchema]


def load_config(path = CONFIG_FILE_PATH):
    with open(path) as f:
        config = load(f.read()).data
    return Configs(**config)
