from typing import List, Optional, Union

from pydantic import BaseModel, Field


class SignalResult(BaseModel):
    name: str
    value: Optional[Union[float, str]] = None
    status: str
    explanation: str


class TechnicalDetails(BaseModel):
    channels_analyzed: List[str] = Field(default_factory=list)
    format_warning: Optional[str] = None
    notes: List[str] = Field(default_factory=list)


class DetectionResponse(BaseModel):
    filename: str
    image_type: str
    width: int
    height: int
    detector_used: str
    target: str
    risk_score: float
    risk_band: str
    confidence_note: str
    signals: List[SignalResult]
    technical: TechnicalDetails