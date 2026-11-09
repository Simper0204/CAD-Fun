from enum import Enum


class FaceType(str, Enum):
    """Geometric surface types accepted by the Version 1 contract."""

    plane = "plane"
    cylinder = "cylinder"
    cone = "cone"
    sphere = "sphere"
    torus = "torus"
    other = "other"


# Stable order used when a face-type error map is built from the union of keys.
FACE_TYPE_ORDER: tuple[str, ...] = tuple(face_type.value for face_type in FaceType)

CRITERION_NAMES: tuple[str, ...] = (
    "volume",
    "surface_area",
    "center_of_mass",
    "bounding_box",
    "number_of_solid_bodies",
    "number_of_solid_faces",
    "number_of_edges",
    "face_types",
)
