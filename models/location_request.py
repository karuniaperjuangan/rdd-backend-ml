from typing import Union, List

from fastapi import FastAPI
from pydantic import BaseModel


class LocationRequestModel(BaseModel):
    locations: list
    times: list

    class Config:
        schema_extra = {
            "example": {
                "locations": [{
                    "microTime": 100000000,
                    "latitude": -4.3,
                    "longitude": 2.1,
                }],
                "times": [
                    0, 0.3, 0.5
                ]
            }
        }