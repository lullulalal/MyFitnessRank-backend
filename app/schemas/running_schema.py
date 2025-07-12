from typing import List, Literal
from pydantic import BaseModel, Field

class RunningRequest(BaseModel):
    record_seconds: float = Field(..., description="User's race completion time in seconds")
    age: int = Field(..., description="User's age at the time of the race")
    gender: Literal["male", "female"] = Field(..., description="User's gender: 'male' for male, 'female' for female")
    distance: str = Field(..., description="Distance of the race in kilometers")
    target_races: List[str] = Field(..., description="List of race IDs to include in percentile comparison")

class HistogramBin(BaseModel):
    time_range_start: int = Field(..., description="Start of the time range in minutes")
    time_range_end: int = Field(..., description="End of the time range in minutes")
    percent: float = Field(..., description="Percentage of participants in this bin (0.0–100.0)")
    count: int = Field(..., description="Number of participants in this bin")
    is_user_bin: bool = Field(..., description="True if the user's record falls within this bin")

class HistogramResult(BaseModel):
    bins: List[HistogramBin] = Field(..., description="List of percentile bins representing performance distribution")
    user_percentile: float = Field(..., description="Percentile position of the user's record within this group")
    age_range_start: int = Field(..., description="Start of the age range for the user")
    age_range_end: int = Field(..., description="End of the age range for the user")

class RunningResponse(BaseModel):
    overall: HistogramResult = Field(..., description="User's percentile compared to all participants")
    by_gender: HistogramResult = Field(..., description="User's percentile compared to participants of the same gender")
    by_gender_age: HistogramResult = Field(..., description="User's percentile compared to participants of the same gender and similar age group")
