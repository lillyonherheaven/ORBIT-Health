from typing import List, Optional
from pydantic import BaseModel, Field

class DailyCheckin(BaseModel):
    astronaut_id: str = Field(..., min_length=1)
    date: str = Field(..., min_length=1)
    physical_status: str = Field(..., min_length=1)
    restedness: str = Field(..., min_length=1)
    stress: str = Field(..., min_length=1)
    mood: str = Field(..., min_length=1)
    symptoms: List[str] = Field(default_factory=list)
    free_text: Optional[str] = None
