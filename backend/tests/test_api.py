import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.questions import load_seed_questions
from app.repository import InMemoryQuestionRepository
from tests.factories import make_question, matching_submission

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_SUBMISSION = (
    REPO_ROOT / "docs_for_agents" / "examples" / "frontend_ex_prob_submit.json"
)


def _client_for(question) -> TestClient:
    app = create_app(repository=InMemoryQuestionRepository([question]))
    return TestClient(app)


def test_assessment_returns_scores_for_a_matching_submission() -> None:
    question = make_question()
    client = _client_for(question)
    response = client.post(
        "/api/v1/assessments",
        json={
            "question_id": question.question_id,
            "parameters": matching_submission(question).model_dump(mode="json"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["question_id"] == "CAD001"
    assert body["overall_score"] == 100.0
    assert set(body["assessment"]) == {
        "volume",
        "surface_area",
        "center_of_mass",
        "bounding_box",
        "number_of_solid_bodies",
        "number_of_solid_faces",
        "number_of_edges",
        "face_types",
    }


def test_seeded_example_submission_is_a_perfect_answer() -> None:
    question = load_seed_questions()[0]
    client = _client_for(question)
    response = client.post(
        "/api/v1/assessments",
        json=json.loads(EXAMPLE_SUBMISSION.read_text(encoding="utf-8")),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["overall_score"] == 100.0
    assert body["assessment"]["volume"] == {"error": 0.0, "score": 100.0}
    assert body["assessment"]["face_types"]["error"] == {"plane": 0}


def test_unknown_question_returns_404() -> None:
    client = _client_for(make_question())
    payload = {
        "question_id": "MISSING",
        "parameters": matching_submission(make_question()).model_dump(mode="json"),
    }
    response = client.post("/api/v1/assessments", json=payload)

    assert response.status_code == 404
    assert response.json() == {
        "error_code": "QUESTION_NOT_FOUND",
        "message": "No question exists with that question_id.",
    }


def test_invalid_json_returns_400() -> None:
    client = _client_for(make_question())
    response = client.post(
        "/api/v1/assessments",
        content=b"{",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "MALFORMED_REQUEST"
    assert "details" in body


@pytest.mark.parametrize(
    "payload_change",
    [
        {"question_id": ""},
        {"question_id": 1},
        {"parameters": {"moment_of_inertia": 1}},
    ],
)
def test_structurally_invalid_submission_returns_422(payload_change: dict) -> None:
    question = make_question()
    payload = {
        "question_id": question.question_id,
        "parameters": matching_submission(question).model_dump(mode="json"),
    }
    if "parameters" in payload_change and payload_change["parameters"] == {
        "moment_of_inertia": 1
    }:
        payload["parameters"]["moment_of_inertia"] = 1
    else:
        payload.update(payload_change)

    response = _client_for(question).post("/api/v1/assessments", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert isinstance(body["details"], list)


@pytest.mark.parametrize(
    "parameters_patch",
    [
        {"volume": -1},
        {"bounding_box": [10, 10, -1]},
        {"number_of_edges": 1.5},
        {"number_of_solid_bodies": True},
        {"face_types": {"smooth": 1}},
        {"center_of_mass": [1, 2]},
    ],
)
def test_semantic_parameter_errors_return_422(parameters_patch: dict) -> None:
    question = make_question()
    parameters = matching_submission(question).model_dump(mode="json")
    parameters.update(parameters_patch)
    response = _client_for(question).post(
        "/api/v1/assessments",
        json={"question_id": question.question_id, "parameters": parameters},
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"


def test_integer_volume_is_accepted() -> None:
    question = make_question()
    parameters = matching_submission(question).model_dump(mode="json")
    parameters["volume"] = 100
    response = _client_for(question).post(
        "/api/v1/assessments",
        json={"question_id": question.question_id, "parameters": parameters},
    )

    assert response.status_code == 200
    assert response.json()["assessment"]["volume"]["score"] == 100.0


def test_invalid_question_configuration_returns_500_without_a_stack_trace() -> None:
    question = make_question()
    question.criteria.volume.tolerance = 0
    response = _client_for(question).post(
        "/api/v1/assessments",
        json={
            "question_id": question.question_id,
            "parameters": matching_submission(question).model_dump(mode="json"),
        },
    )

    assert response.status_code == 500
    body = response.json()
    assert body["error_code"] == "QUESTION_CONFIG_INVALID"
    assert "Traceback" not in response.text
    assert body["details"][0]["loc"] == ["volume", "tolerance"]
