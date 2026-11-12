"""Compare submitted parameters with a question's expected values.

The formulas come from docs_for_agents/SCORING_SYSTEM.md. Tolerances, weights,
and comparison methods are read from the question configuration. This module
does not choose those values.
"""

from decimal import Decimal, ROUND_HALF_UP

from app.constants import CRITERION_NAMES, FACE_TYPE_ORDER
from app.errors import QuestionConfigError
from app.questions import CountCriterion, QuestionConfig
from app.schemas import (
    AssessmentBreakdown,
    AssessmentResponse,
    CountAssessment,
    FaceTypesAssessment,
    ScalarAssessment,
    SubmittedParameters,
    VectorAssessment,
)

SCORE_INCREMENT = Decimal("0.01")
MEASUREMENT_INCREMENT = Decimal("0.000001")


def assess(question: QuestionConfig, parameters: SubmittedParameters) -> AssessmentResponse:
    raw_scores: list[float] = []
    weights: list[float] = []
    scored: dict[str, tuple[object, float]] = {}

    for name in CRITERION_NAMES:
        criterion = getattr(question.criteria, name)
        submitted = getattr(parameters, name)
        error, raw_score = _score_criterion(name, submitted, criterion)
        scored[name] = (error, round_score(raw_score))
        if criterion.enabled:
            raw_scores.append(raw_score)
            weights.append(criterion.weight)

    total_weight = sum(weights)
    if total_weight <= 0:
        raise QuestionConfigError(
            "Question configuration is invalid.",
            details=[{"msg": "at least one enabled criterion must have a positive weight"}],
        )

    # Overall uses the unrounded criterion scores. Only the displayed value is rounded.
    overall = sum(score * weight for score, weight in zip(raw_scores, weights)) / total_weight
    breakdown = AssessmentBreakdown(
        volume=ScalarAssessment(error=scored["volume"][0], score=scored["volume"][1]),
        surface_area=ScalarAssessment(
            error=scored["surface_area"][0], score=scored["surface_area"][1]
        ),
        center_of_mass=VectorAssessment(
            error=scored["center_of_mass"][0], score=scored["center_of_mass"][1]
        ),
        bounding_box=VectorAssessment(
            error=scored["bounding_box"][0], score=scored["bounding_box"][1]
        ),
        number_of_solid_bodies=CountAssessment(
            error=scored["number_of_solid_bodies"][0],
            score=scored["number_of_solid_bodies"][1],
        ),
        number_of_solid_faces=CountAssessment(
            error=scored["number_of_solid_faces"][0],
            score=scored["number_of_solid_faces"][1],
        ),
        number_of_edges=CountAssessment(
            error=scored["number_of_edges"][0], score=scored["number_of_edges"][1]
        ),
        face_types=FaceTypesAssessment(
            error=scored["face_types"][0], score=scored["face_types"][1]
        ),
    )
    return AssessmentResponse(
        question_id=question.question_id,
        assessment=breakdown,
        overall_score=round_score(overall),
    )


def _score_criterion(name: str, submitted: object, criterion: object) -> tuple[object, float]:
    comparison = criterion.comparison
    if comparison == "percentage":
        expected = criterion.expected
        error = abs(submitted - expected) / abs(expected) * 100
        return round_measurement(error), _tolerance_score(error, criterion.tolerance, name)
    if comparison == "absolute":
        error = abs(submitted - criterion.expected)
        return round_measurement(error), _tolerance_score(error, criterion.tolerance, name)
    if comparison == "vector_max_component":
        components = [
            abs(submitted_component - expected_component)
            for submitted_component, expected_component in zip(
                submitted, criterion.expected, strict=True
            )
        ]
        reported = [round_measurement(component) for component in components]
        return reported, _tolerance_score(max(components), criterion.tolerance, name)
    if comparison == "count_tolerance":
        error = _count_error(submitted, criterion)
        return error, _tolerance_score(error, criterion.tolerance, name)
    if comparison == "exact_match":
        error = _count_error(submitted, criterion)
        return error, 100.0 if error == 0 else 0.0
    if comparison == "face_types_max":
        error_map = _face_type_errors(submitted, criterion.expected)
        normalized = max(error_map.values(), default=0)
        return error_map, _tolerance_score(normalized, criterion.tolerance, name)
    raise QuestionConfigError(
        "Question configuration is invalid.",
        details=[{"loc": [name, "comparison"], "msg": "unsupported comparison method"}],
    )


def _count_error(submitted: object, criterion: CountCriterion) -> int:
    return abs(int(submitted) - int(criterion.expected))


def _face_type_errors(submitted: dict, expected: dict) -> dict[str, int]:
    submitted_counts = {_face_type_name(key): int(value) for key, value in submitted.items()}
    expected_counts = {_face_type_name(key): int(value) for key, value in expected.items()}
    keys = [
        name
        for name in FACE_TYPE_ORDER
        if name in submitted_counts or name in expected_counts
    ]
    return {
        name: abs(submitted_counts.get(name, 0) - expected_counts.get(name, 0))
        for name in keys
    }


def _face_type_name(key: object) -> str:
    return key.value if hasattr(key, "value") else str(key)


def _tolerance_score(normalized_error: float, tolerance: float | None, criterion: str) -> float:
    """parameter_score = max(0, 100 * (1 - normalized_error / tolerance))."""
    if tolerance is None or tolerance <= 0:
        raise QuestionConfigError(
            "Question configuration is invalid.",
            details=[{"loc": [criterion, "tolerance"], "msg": "tolerance must be greater than zero"}],
        )
    return _clamp_score(100.0 * (1.0 - normalized_error / tolerance))


def _clamp_score(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 100:
        return 100.0
    return value


def round_score(value: float) -> float:
    """Round a displayed score to two decimal places, half up."""
    clamped = _clamp_score(value)
    quantized = Decimal(format(clamped, ".10f")).quantize(SCORE_INCREMENT, rounding=ROUND_HALF_UP)
    return float(quantized)


def round_measurement(value: float) -> float:
    quantized = Decimal(format(value, ".12f")).quantize(
        MEASUREMENT_INCREMENT, rounding=ROUND_HALF_UP
    )
    return float(quantized)
