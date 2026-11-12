from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.constants import FaceType

StrictCount = Annotated[int, Field(ge=0, strict=True)]
FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]
NonNegativeFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Score = Annotated[float, Field(ge=0, le=100)]

Coordinate = Annotated[list[FiniteFloat], Field(min_length=3, max_length=3)]
NonNegativeVector = Annotated[list[NonNegativeFloat], Field(min_length=3, max_length=3)]


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SubmittedParameters(APIModel):
    volume: NonNegativeFloat
    surface_area: NonNegativeFloat
    center_of_mass: Coordinate
    bounding_box: NonNegativeVector
    number_of_solid_bodies: StrictCount
    number_of_solid_faces: StrictCount
    number_of_edges: StrictCount
    face_types: dict[FaceType, StrictCount]


class AssessmentSubmission(APIModel):
    question_id: Annotated[str, Field(strict=True, min_length=1)]
    parameters: SubmittedParameters


class ScalarAssessment(APIModel):
    error: NonNegativeFloat
    score: Score


class VectorAssessment(APIModel):
    error: NonNegativeVector
    score: Score


class CountAssessment(APIModel):
    error: StrictCount
    score: Score


class FaceTypesAssessment(APIModel):
    error: dict[FaceType, StrictCount]
    score: Score


class AssessmentBreakdown(APIModel):
    volume: ScalarAssessment
    surface_area: ScalarAssessment
    center_of_mass: VectorAssessment
    bounding_box: VectorAssessment
    number_of_solid_bodies: CountAssessment
    number_of_solid_faces: CountAssessment
    number_of_edges: CountAssessment
    face_types: FaceTypesAssessment


class AssessmentResponse(APIModel):
    question_id: str
    assessment: AssessmentBreakdown
    overall_score: Score


class ErrorResponse(APIModel):
    error_code: str
    message: str
    details: list[dict[str, object]] | None = None
