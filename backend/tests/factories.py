from app.questions import QuestionConfig
from app.schemas import SubmittedParameters


def make_question(**overrides: dict) -> QuestionConfig:
    criteria = {
        "volume": {
            "enabled": True,
            "expected": 100,
            "comparison": "percentage",
            "tolerance": 10,
            "weight": 1,
        },
        "surface_area": {
            "enabled": True,
            "expected": 100,
            "comparison": "percentage",
            "tolerance": 10,
            "weight": 1,
        },
        "center_of_mass": {
            "enabled": True,
            "expected": [0, 0, 0],
            "comparison": "vector_max_component",
            "tolerance": 10,
            "weight": 1,
        },
        "bounding_box": {
            "enabled": True,
            "expected": [10, 10, 10],
            "comparison": "vector_max_component",
            "tolerance": 10,
            "weight": 1,
        },
        "number_of_solid_bodies": {
            "enabled": True,
            "expected": 1,
            "comparison": "exact_match",
            "weight": 1,
        },
        "number_of_solid_faces": {
            "enabled": True,
            "expected": 6,
            "comparison": "count_tolerance",
            "tolerance": 4,
            "weight": 1,
        },
        "number_of_edges": {
            "enabled": True,
            "expected": 12,
            "comparison": "count_tolerance",
            "tolerance": 4,
            "weight": 1,
        },
        "face_types": {
            "enabled": True,
            "expected": {"plane": 6},
            "comparison": "face_types_max",
            "tolerance": 4,
            "weight": 1,
        },
    }
    for name, patch in overrides.items():
        criteria[name].update(patch)
    return QuestionConfig.model_validate(
        {
            "question_id": "CAD001",
            "title": "Test question",
            "coordinate_frame": "Right-handed model frame",
            "axis_order": "x, y, z",
            "criteria": criteria,
        }
    )


def matching_submission(question: QuestionConfig) -> SubmittedParameters:
    criteria = question.criteria.model_dump(mode="json")
    return SubmittedParameters.model_validate(
        {
            "volume": criteria["volume"]["expected"],
            "surface_area": criteria["surface_area"]["expected"],
            "center_of_mass": criteria["center_of_mass"]["expected"],
            "bounding_box": criteria["bounding_box"]["expected"],
            "number_of_solid_bodies": criteria["number_of_solid_bodies"]["expected"],
            "number_of_solid_faces": criteria["number_of_solid_faces"]["expected"],
            "number_of_edges": criteria["number_of_edges"]["expected"],
            "face_types": criteria["face_types"]["expected"],
        }
    )
