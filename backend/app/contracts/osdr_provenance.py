from typing import Optional
from pydantic import BaseModel, Field

class OSDRProvenance(BaseModel):
    study_id: str = Field(..., min_length=1)
    study_link: str = Field(..., min_length=1)
    version: str = "v1"
    organism_model: str = Field(..., min_length=1)
    tissue: str = Field(..., min_length=1)
    assay: str = Field(..., min_length=1)
    source_file: str = Field(..., min_length=1)
    source_column: str = Field(..., min_length=1)
    original_unit: str = Field(..., min_length=1)
    normalized_unit: str = Field(..., min_length=1)
    transformation: str = "identity_or_baseline_normalized"
    evidence_limitation: str = Field(..., min_length=1)
    license_status: str = "NASA_Open_Science_OSDR"
