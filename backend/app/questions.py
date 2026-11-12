import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.constants import CRITERION_NAMES, FaceType
from app.errors import QuestionConfigError, sanitize_errors
from app.schemas import Coordinate, NonNegativeFloat, StrictCount

SEED_PATH = Path(__file__).resolve().parent / "seed" / "questions.json"

PositiveTolerance = Annotated[float, Field(gt=0, allow_inf_nan=False)]
NonNegativeWeight = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class QuestionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ScalarCriterion(QuestionModel):
    enabled: bool
    expected: NonNegativeFloat
    comparison: Literal["percentage", "absolute"]
    tolerance: PositiveTolerance
    weight: NonNegativeWeight

    @model_validator(mode="after")
    def percentage_requires_nonzero_expected(self) -> "ScalarCriterion":
        if self.comparison == "percentage" and self.expected == 0:
            raise ValueError(
                "percentage comparison is undefined when the expected value is zero; use absolute"
            )
        return self


class VectorCriterion(QuestionModel):
    enabled: bool
    expected: Coordinate
    comparison: Literal["vector_max_component"]
    tolerance: PositiveTolerance
    weight: NonNegativeWeight


class CountCriterion(QuestionModel):
    enabled: bool
    expected: StrictCount
    comparison: Literal["count_tolerance", "exact_match"]
    tolerance: PositiveTolerance | None = None
    weight: NonNegativeWeight

    @model_validator(mode="after")
    def tolerance_matches_comparison(self) -> "CountCriterion":
        if self.comparison == "count_tolerance" and self.tolerance is None:
            raise ValueError("count_tolerance requires a tolerance greater than zero")
        if self.comparison == "exact_match" and self.tolerance is not None:
            raise ValueError("exact_match does not use a tolerance")
        return self


class FaceTypesCriterion(QuestionModel):
    enabled: bool
    expected: dict[FaceType, StrictCount]
    comparison: Literal["face_types_max"]
    tolerance: PositiveTolerance
    weight: NonNegativeWeight


class QuestionCriteria(QuestionModel):
    volume: ScalarCriterion
    surface_area: ScalarCriterion
    center_of_mass: VectorCriterion
    bounding_box: VectorCriterion
    number_of_solid_bodies: CountCriterion
    number_of_solid_faces: CountCriterion
    number_of_edges: CountCriterion
    face_types: FaceTypesCriterion

    @model_validator(mode="after")
    def bounding_box_expected_is_non_negative(self) -> "QuestionCriteria":
        if any(component < 0 for component in self.bounding_box.expected):
            raise ValueError("bounding_box expected dimensions must be greater than or equal to 0")
        return self


class QuestionConfig(QuestionModel):
    question_id: Annotated[str, Field(strict=True, min_length=1)]
    title: Annotated[str, Field(strict=True, min_length=1)]
    coordinate_frame: Annotated[str, Field(strict=True, min_length=1)]
    axis_order: Annotated[str, Field(strict=True, min_length=1)]
    criteria: QuestionCriteria

    @model_validator(mode="after")
    def at_least_one_positive_weight(self) -> "QuestionConfig":
        total_weight = sum(
            getattr(self.criteria, name).weight
            for name in CRITERION_NAMES
            if getattr(self.criteria, name).enabled
        )
        if total_weight <= 0:
            raise ValueError("at least one enabled criterion must have a positive weight")
        return self


def load_seed_questions(path: Path | None = None) -> list[QuestionConfig]:
    seed_path = path or SEED_PATH
    payload = json.loads(seed_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("questions"), list):
        raise QuestionConfigError("Seed file must be an object with a questions array.")

    questions: list[QuestionConfig] = []
    for item in payload["questions"]:
        try:
            questions.append(QuestionConfig.model_validate(item))
        except ValidationError as exc:
            raise QuestionConfigError(
                "Seed question configuration is invalid.",
                details=sanitize_errors(exc.errors()),
            ) from exc

    ids = [question.question_id for question in questions]
    if len(ids) != len(set(ids)):
        raise QuestionConfigError("Seed contains duplicate question_id values.")
    return questions
