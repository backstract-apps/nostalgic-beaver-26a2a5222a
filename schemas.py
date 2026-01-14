from pydantic import BaseModel,Field,field_validator

import datetime

import uuid

from typing import Any, Dict, List,Optional,Tuple,Union

import re

class MaysonRequestLogger(BaseModel):
    ts_utc: datetime.time
    method: Optional[str]=None
    path: Optional[str]=None
    status_code: Optional[Union[int, float]]=None
    duration_ms: Optional[float]=None
    client_ip: Optional[str]=None
    user_agent: Optional[str]=None
    content_length: Optional[Union[int, float]]=None
    style: Optional[str]=None
    message: Optional[str]=None


class ReadMaysonRequestLogger(BaseModel):
    ts_utc: datetime.time
    method: Optional[str]=None
    path: Optional[str]=None
    status_code: Optional[Union[int, float]]=None
    duration_ms: Optional[float]=None
    client_ip: Optional[str]=None
    user_agent: Optional[str]=None
    content_length: Optional[Union[int, float]]=None
    style: Optional[str]=None
    message: Optional[str]=None
    class Config:
        from_attributes = True


class Users(BaseModel):
    name: str
    email: str


class ReadUsers(BaseModel):
    name: str
    email: str
    class Config:
        from_attributes = True


class ItemsSold(BaseModel):
    quantity: int
    price_per_item: int
    price: Optional[float]=None


class ReadItemsSold(BaseModel):
    quantity: int
    price_per_item: int
    price: Optional[float]=None
    class Config:
        from_attributes = True




# Query Parameter Validation Schemas

class GetRandomQueryParams(BaseModel):
    """Query parameter validation for get_random"""
    var_1: Optional[Union[int, float]] = Field(None)
    var_2: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True


class GetFloorQueryParams(BaseModel):
    """Query parameter validation for get_floor"""
    var_1: Optional[Union[int, float]] = Field(None)
    var_2: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True


class GetArithmeticQueryParams(BaseModel):
    """Query parameter validation for get_arithmetic"""
    var_1: Optional[Union[int, float]] = Field(None)
    var_2: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True


class GetRoundQueryParams(BaseModel):
    """Query parameter validation for get_round"""
    var_1: Optional[Union[int, float]] = Field(None)
    var_2: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True


class GetCeilQueryParams(BaseModel):
    """Query parameter validation for get_ceil"""
    var_1: Optional[Union[int, float]] = Field(None)
    var_2: Optional[Union[int, float]] = Field(None)

    class Config:
        populate_by_name = True
