from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ScoringStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"

class ScoringRequest(BaseModel):
    application_id: int
    user_id: int
    inn: str = Field(..., pattern=r'^\d{12}$')
    passport_number: str = Field(..., pattern=r'^\d{10}$')
    loan_amount: float = Field(..., gt=0)
    loan_term: int = Field(..., gt=0)
    user_salary: Optional[float] = Field(None, ge=0)  # ✅ Добавляем зарплату

class ScoringResult(BaseModel):
    application_id: int
    user_id: int
    status: ScoringStatus
    score: int = Field(..., ge=0, le=1000)
    approved_amount: Optional[float] = None
    approved_term: Optional[int] = None
    interest_rate: Optional[float] = None
    monthly_payment: Optional[float] = None
    rejection_reason: Optional[str] = None
    insurance_required: bool = False
    details: Dict[str, Any] = {}

class ScoringResponse(BaseModel):
    success: bool
    data: Optional[ScoringResult] = None
    error: Optional[str] = None
    timestamp: datetime

class ScoringConfig(BaseModel):
    min_score_approval: int = 650
    max_loan_amount: float = 5000000
    min_loan_amount: float = 10000
    max_loan_term: int = 60
    min_loan_term: int = 6
    base_interest_rate: float = 12.5