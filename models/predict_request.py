from typing import Union, List

from fastapi import FastAPI
from pydantic import BaseModel


class PredictRequestModel(BaseModel):
    url: str

    class Config:
        schema_extra = {
            "example": {
                "url": "https://github-production-user-asset-6210df.s3.amazonaws.com/60359573/262746519-f168823e-7922-415a-b429-578badf5c356.mp4"
            }
        }