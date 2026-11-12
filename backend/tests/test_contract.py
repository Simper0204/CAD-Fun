import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.errors import QuestionConfigError
from app.questions import load_seed_questions
from app.schemas import AssessmentResponse, AssessmentSubmission

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "docs_for_agents" / "examples"


def test_frontend_example_matches_the_request_schema() -> None:
    payload = json.loads((EXAMPLES / "frontend_ex_prob_submit.json").read_text(encoding="utf-8"))
    submission = AssessmentSubmission.model_validate(payload)
    assert submission.question_id == "CAD001"


def test_backend_example_matches_the_response_schema() -> None:
    payload = json.loads((EXAMPLES / "backend_ex_prob_response.json").read_text(encoding="utf-8"))
    response = AssessmentResponse.model_validate(payload)
    assert response.overall_score == 94.0


def test_seed_question_uses_the_example_submission_as_its_expected_values() -> None:
    question = load_seed_questions()[0]
    payload = json.loads((EXAMPLES / "frontend_ex_prob_submit.json").read_text(encoding="utf-8"))
    submitted = payload["parameters"]
    criteria = question.criteria

    assert question.question_id == "CAD001"
    assert criteria.volume.expected == submitted["volume"]
    assert criteria.surface_area.expected == submitted["surface_area"]
    assert criteria.center_of_mass.expected == submitted["center_of_mass"]
    assert criteria.bounding_box.expected == submitted["bounding_box"]
    assert criteria.number_of_solid_bodies.expected == submitted["number_of_solid_bodies"]
    assert criteria.number_of_solid_faces.expected == submitted["number_of_solid_faces"]
    assert criteria.number_of_edges.expected == submitted["number_of_edges"]
    assert criteria.face_types.expected == submitted["face_types"]


def test_duplicate_seed_ids_are_rejected(tmp_path: Path) -> None:
    question = json.loads(
        (Path(__file__).resolve().parents[1] / "app" / "seed" / "questions.json").read_text(
            encoding="utf-8"
        )
    )["questions"][0]
    path = tmp_path / "questions.json"
    path.write_text(json.dumps({"questions": [question, question]}), encoding="utf-8")

    with pytest.raises(QuestionConfigError, match="duplicate"):
        load_seed_questions(path)


def test_human_example_with_moment_of_inertia_is_not_a_valid_submission() -> None:
    payload = json.loads(
        (REPO_ROOT / "doc_for_humans" / "frontend_ex_prob_submit.json").read_text(encoding="utf-8")
    )
    with pytest.raises(ValidationError):
        AssessmentSubmission.model_validate(payload)
