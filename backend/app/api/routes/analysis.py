import logging
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Response

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
    response: Response,
) -> AnalysisResponse:
    request_id = str(uuid4())

    start_time = perf_counter()

    try:
        result = service.analyze(
            request.question
        )

        execution_time_ms = round(
            (perf_counter() - start_time) * 1000,
            2,
        )

        result.request_id = request_id
        result.execution_time_ms = execution_time_ms

        response.headers["X-Request-ID"] = request_id

        logger.info(
            (
                "analysis_completed "
                "request_id=%s "
                "tools=%s "
                "retry_count=%s "
                "execution_time_ms=%s "
                "validation_errors=%s"
            ),
            request_id,
            ",".join(result.selected_tools) or "none",
            result.retry_count,
            execution_time_ms,
            len(result.validation_errors),
        )

        return result

    except ValueError as exc:
        execution_time_ms = round(
            (perf_counter() - start_time) * 1000,
            2,
        )

        response.headers["X-Request-ID"] = request_id

        logger.warning(
            (
                "analysis_validation_error "
                "request_id=%s "
                "execution_time_ms=%s "
                "error=%s"
            ),
            request_id,
            execution_time_ms,
            str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        execution_time_ms = round(
            (perf_counter() - start_time) * 1000,
            2,
        )

        response.headers["X-Request-ID"] = request_id

        logger.exception(
            (
                "analysis_failed "
                "request_id=%s "
                "execution_time_ms=%s "
                "question=%s"
            ),
            request_id,
            execution_time_ms,
            request.question,
        )

        raise HTTPException(
            status_code=500,
            detail="Analysis failed.",
        )