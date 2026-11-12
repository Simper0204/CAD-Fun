import pytest
from pydantic import ValidationError

from app.schemas import SubmittedParameters
from app.scoring import assess
from tests.factories import make_question, matching_submission


def _assess(question, **patches):
    data = matching_submission(question).model_dump(mode="json")
    data.update(patches)
    return assess(question, SubmittedParameters.model_validate(data))


def test_exact_submission_scores_100() -> None:
    question = make_question()
    result = assess(question, matching_submission(question))

    assert result.overall_score == 100.0
    assert result.assessment.volume.error == 0.0
    assert result.assessment.volume.score == 100.0
    assert result.assessment.center_of_mass.error == [0.0, 0.0, 0.0]
    assert result.assessment.number_of_solid_bodies.error == 0
    assert result.assessment.face_types.error == {"plane": 0}


def test_percentage_error_and_overall_use_unrounded_scores() -> None:
    question = make_question(volume={"tolerance": 3})
    result = _assess(question, volume=101)

    assert result.assessment.volume.error == 1.0
    assert result.assessment.volume.score == 66.67
    assert result.overall_score == 95.83


def test_error_beyond_tolerance_scores_zero() -> None:
    question = make_question()
    result = _assess(question, volume=150)

    assert result.assessment.volume.error == 50.0
    assert result.assessment.volume.score == 0.0


def test_absolute_comparison_when_expected_value_is_zero() -> None:
    question = make_question(
        volume={"expected": 0, "comparison": "absolute", "tolerance": 4}
    )
    result = _assess(question, volume=2)

    assert result.assessment.volume.error == 2.0
    assert result.assessment.volume.score == 50.0


def test_percentage_comparison_rejects_zero_expected_value() -> None:
    with pytest.raises(ValidationError):
        make_question(volume={"expected": 0, "comparison": "percentage"})


def test_vector_score_uses_maximum_component() -> None:
    question = make_question()
    result = _assess(question, center_of_mass=[1, 3, 0])

    assert result.assessment.center_of_mass.error == [1.0, 3.0, 0.0]
    assert result.assessment.center_of_mass.score == 70.0


def test_negative_center_of_mass_is_a_valid_coordinate() -> None:
    question = make_question(center_of_mass={"expected": [-1, 0, 0]})
    result = _assess(question, center_of_mass=[0, 0, 0])

    assert result.assessment.center_of_mass.error == [1.0, 0.0, 0.0]
    assert result.assessment.center_of_mass.score == 90.0


def test_exact_count_match_and_count_tolerance() -> None:
    question = make_question()
    result = _assess(question, number_of_solid_bodies=2, number_of_solid_faces=7)

    assert result.assessment.number_of_solid_bodies.error == 1
    assert result.assessment.number_of_solid_bodies.score == 0.0
    assert result.assessment.number_of_solid_faces.error == 1
    assert result.assessment.number_of_solid_faces.score == 75.0


def test_face_type_error_includes_types_missing_from_either_map() -> None:
    question = make_question()
    result = _assess(question, face_types={"cylinder": 1})

    assert result.assessment.face_types.error == {"plane": 6, "cylinder": 1}
    assert result.assessment.face_types.score == 0.0


def test_disabled_criterion_is_returned_and_excluded_from_overall_score() -> None:
    question = make_question(volume={"enabled": False})
    result = _assess(question, volume=0)

    assert result.assessment.volume.score == 0.0
    assert result.overall_score == 100.0


def test_weights_change_the_overall_score() -> None:
    question = make_question(
        volume={"weight": 1},
        surface_area={"weight": 3},
        center_of_mass={"enabled": False},
        bounding_box={"enabled": False},
        number_of_solid_bodies={"enabled": False},
        number_of_solid_faces={"enabled": False},
        number_of_edges={"enabled": False},
        face_types={"enabled": False},
    )
    result = _assess(question, volume=90)

    assert result.assessment.volume.score == 0.0
    assert result.assessment.surface_area.score == 100.0
    assert result.overall_score == 75.0


def test_negative_expected_bounding_box_is_invalid_configuration() -> None:
    with pytest.raises(ValidationError):
        make_question(bounding_box={"expected": [10, -1, 10]})
