from fastapi import APIRouter, HTTPException, status
import logging
from datetime import datetime

from app.schemas.scoring import ScoringRequest, ScoringResponse, ScoringResult
from app.core.scoring_engine import ScoringEngine

router = APIRouter()
logger = logging.getLogger(__name__)

scoring_engine = ScoringEngine()

@router.post("/evaluate", response_model=ScoringResponse)
async def evaluate_application(request: ScoringRequest):
    """
    Эмуляция банковского скоринга
    """
    try:
        logger.info(f"Processing scoring for application {request.application_id}")
        
        # Выполняем скоринг
        result = scoring_engine.evaluate_application(request)
        
        logger.info(f"Scoring completed for application {request.application_id}: {result.status}")
        
        return ScoringResponse(
            success=True,
            data=result,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Scoring error for application {request.application_id}: {str(e)}")
        return ScoringResponse(
            success=False,
            error=f"Scoring processing failed: {str(e)}",
            timestamp=datetime.utcnow()
        )

@router.get("/config")
async def get_scoring_config():
    """Получить текущую конфигурацию скоринга"""
    return {
        "min_score_approval": scoring_engine.config.min_score_approval,
        "max_loan_amount": scoring_engine.config.max_loan_amount,
        "base_interest_rate": scoring_engine.config.base_interest_rate
    }

@router.post("/simulate/{status}")
async def simulate_scoring_result(
    status: str,
    request: ScoringRequest
):
    """
    Эмуляция конкретного результата скоринга (для тестирования)
    """
    from app.schemas.scoring import ScoringStatus
    
    status_map = {
        "approved": ScoringStatus.APPROVED,
        "rejected": ScoringStatus.REJECTED,
        "manual": ScoringStatus.MANUAL_REVIEW
    }
    
    if status not in status_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Use: approved, rejected, or manual"
        )
    
    # Создаем фиктивный результат
    result = ScoringResult(
        application_id=request.application_id,
        user_id=request.user_id,
        status=status_map[status],
        score=800 if status == "approved" else 400,
        approved_amount=request.loan_amount if status == "approved" else None,
        approved_term=request.loan_term if status == "approved" else None,
        interest_rate=10.5 if status == "approved" else None,
        monthly_payment=15000 if status == "approved" else None,
        rejection_reason="Тестовый отказ" if status == "rejected" else None,
        insurance_required=False,
        details={"simulated": True}
    )
    
    return ScoringResponse(
        success=True,
        data=result,
        timestamp=datetime.utcnow()
    )