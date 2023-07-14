from typing import Optional, Any, Dict
from datetime import datetime

from pydantic import BaseModel, validator


class DatabaseEntityModel(BaseModel):
    name: str
    value: Dict[str, Any]

    @validator('name')
    def validate_len_name(cls, value):
        if len(value) < 2:
            raise ValueError('Поле "name" недостаточной длины')
        if len(value) > 150:
            raise ValueError('Поле "name" слишком длинное')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Vitya Kisliy",
                "value": {
                    "name": "Peter Thiel",
                    "verified": "asdf"
                }
            }
        }


class DatabaseEntityResponseModel(BaseModel):
    id: int
    name: str
    value: str
    date_update: Optional[datetime] = None


class DatabaseListEntitiesResponseModel(BaseModel):
    data: list[DatabaseEntityResponseModel]
