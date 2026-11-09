from fastapi import APIRouter, Depends, Request

from app.errors import APIError, QuestionConfigError, QuestionNotFound
from app.repository import QuestionRepository
from app.schemas import AssessmentResponse, AssessmentSubmission, ErrorResponse
from app.scoring import assess

router = APIRouter()


def get_repository(request: Request) -> QuestionRepository:
    return request.app.state.questions


@router.post(
    "/assessments",
    response_model=AssessmentResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Submit CAD model parameters for assessment",
)
def submit_assessment(
    submission: AssessmentSubmission,
    repository: QuestionRepository = Depends(get_repository),
) -> AssessmentResponse:
    try:
        question = repository.get(submission.question_id)
    except QuestionNotFound:
        raise APIError(
            status_code=404,
            error_code="QUESTION_NOT_FOUND",
            message="No question exists with that question_id.",
        ) from None
    except QuestionConfigError as exc:
        raise APIError(
            status_code=500,
            error_code="QUESTION_CONFIG_INVALID",
            message=exc.message,
            details=exc.details,
        ) from exc

    try:
        return assess(question, submission.parameters)
    except QuestionConfigError as exc:
        raise APIError(
            status_code=500,
            error_code="QUESTION_CONFIG_INVALID",
            message=exc.message,
            details=exc.details,
        ) from exc
