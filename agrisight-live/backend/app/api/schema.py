"""
Pydantic schemas for API requests and responses.
Expected env vars: None
Testing tips: Use these models to validate mock responses in tests.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class UrgencyLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float
    label: str
    score: float

class AnalysisResult(BaseModel):
    disease_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bounding_boxes: List[BoundingBox]
    recommended_actions: List[str]
    urgency_level: UrgencyLevel
    source_images: List[str]
    session_id: str
    timestamp: str

class SessionCreateResponse(BaseModel):
    session_id: str

class FeedbackRequest(BaseModel):
    correct: bool
    notes: Optional[str] = None
