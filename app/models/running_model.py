from sqlmodel import SQLModel, Field
from typing import Optional


class RunningPercentileBin(SQLModel, table=True):
    race_id: str = Field(primary_key=True)
    race_year: Optional[int] = Field(default=None, primary_key=True)
    distance: str = Field(primary_key=True)
    gender: str = Field(primary_key=True)
    age_group_start: int = Field(primary_key=True)
    percentile_start: int = Field(primary_key=True)
    age_group_end: int = Field(primary_key=True)
    percentile_end: int = Field(primary_key=True)

    finish_seconds_min: float
    finish_seconds_max: float
    count: int
