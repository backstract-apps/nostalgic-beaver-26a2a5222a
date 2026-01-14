from sqlalchemy.orm import Session, aliased
from database import SessionLocal
from sqlalchemy import and_, or_
from typing import *
from fastapi import Request, UploadFile, HTTPException
import models, schemas
import boto3
import jwt
from datetime import datetime
import requests
import math
import random
import asyncio
from pathlib import Path


def convert_to_datetime(date_string):
    if date_string is None:
        return datetime.now()
    from fastapi import HTTPException

    if "T" in date_string:
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except ValueError:
            date_part = date_string.split("T")[0]
            try:
                return datetime.strptime(date_part, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail=f"Improper format in datetime: {date_string}",
                )
    else:
        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=422, detail=f"Improper format in datetime: {date_string}"
            )


async def get_random(
    request: Request, db: Session, var_1: Union[int, float], var_2: Union[int, float]
):
    header_mayson: str = request.headers.get("header-mayson")

    var_1 = random.randint(int(0), int(69))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"var_1": var_1, "var_2": var_2},
    }
    return res


async def get_floor(
    request: Request, db: Session, var_1: Union[int, float], var_2: Union[int, float]
):

    var_2 = math.floor(var_1)

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"var_1": var_1, "var_2": var_2},
    }
    return res


async def get_arithmetic(
    request: Request, db: Session, var_1: Union[int, float], var_2: Union[int, float]
):
    header_fghj: str = request.headers.get("header-fghj")

    var_2 = var_1

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"var_1": var_1, "var_2": var_2},
    }
    return res


async def get_round(
    request: Request, db: Session, var_1: Union[int, float], var_2: Union[int, float]
):

    var_2 = math.ceil(var_1)

    var_2 = round(var_1, 2)

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"var_1": var_1, "var_2": var_2},
    }
    return res


async def get_ceil(
    request: Request, db: Session, var_1: Union[int, float], var_2: Union[int, float]
):

    var_2 = math.ceil(var_1)

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"var_1": var_1, "var_2": var_2},
    }
    return res
