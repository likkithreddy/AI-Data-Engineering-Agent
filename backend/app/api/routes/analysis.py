import logging

from fastapi import APIRouter, HTTPException

from app.agent.graph import default_insight_generator
from app.schemas.api import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import AnalysisService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


service = AnalysisService(
    insight_generator=default_insight_generator,
)


@router.post(
    "",
    response_model=AnalysisResponse,
)
def analyze(
    request: AnalysisRequest,
) -> AnalysisResponse:
    try:
        return service.analyze(
            request.question
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Analysis failed for question: %s",
            request.question,
        )

        raise HTTPException(
            status_code=500,
            detail="Analysis failed.",
        )