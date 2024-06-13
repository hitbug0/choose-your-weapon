from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator  # todo: 非推奨のvalidatorを修正する

from .constants import STATUS_OPTIONS


class RowData(BaseModel):
    uuid: Optional[str] = str(uuid4())
    id_by_user: str
    name: str
    type: str
    size_x: float = Field(gt=0)
    size_y: float = Field(gt=0)
    size_z: float = Field(gt=0)
    remarks: str
    status: Optional[str] = STATUS_OPTIONS[0]

    @validator("status")
    def check_status(cls, v):
        allowed_statuses = set(STATUS_OPTIONS)
        if v not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")
        return v


class TableData(BaseModel):
    data: List[RowData]
    message: Optional[str] = ""
