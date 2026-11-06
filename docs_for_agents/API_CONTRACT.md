# CAD Fun — API Contract (Version 1 draft)

## 1. Purpose

This document defines how the CAD Fun frontend and backend communicate.

The frontend collects a user's CAD model parameters and submits them to the backend. The backend validates the submission, compares it with the expected values for the question, calculates scores, and returns an assessment.

## 2. Source-of-truth documents

- `openapi.yaml` is authoritative for endpoint paths, HTTP methods, request/response schemas, field names, types, and documented status codes.
- `SCORING_SYSTEM.md` is authoritative for comparison and scoring behavior.
- `examples/frontend_ex_prob_submit.json` and `examples/backend_ex_prob_response.json` illustrate representative payloads. They are examples, not files that the website reads or writes for every submission.

If an implementation needs a change to the contract, both frontend and backend must be considered. The project lead must approve the change before it is merged.

## 3. Communication conventions

| Item | Version 1 agreement |
|---|---|
| Protocol | HTTP during local development; HTTPS in production |
| Data format | JSON |
| Character encoding | UTF-8 |
| API prefix | `/api/v1` |
| Local backend base URL | `http://localhost:8000` |
| Content type | `application/json` |
| Assessment submission | `POST /api/v1/assessments` |

`/api/v1` is a URL path prefix, not a folder on disk. The backend registers routes under this prefix. The frontend uses the full base URL plus the route path.

The local base URL is a development default. Production deployment will use a different host, configured outside the source code (for example, through an environment variable).

## 4. Assessment submission

The frontend sends one JSON request to:

`POST /api/v1/assessments`

The request contains:
- `question_id`: identifier of the question being answered.
- `parameters`: the user's measured or reported model parameters.

The frontend must not send its own score as an authoritative result. The backend calculates the scores.

The request shape is demonstrated in `examples/frontend_ex_prob_submit.json` and formally defined by the `AssessmentSubmission` schema in `openapi.yaml`.

## 5. Assessment response

On successful assessment, the backend returns:
- `question_id`
- `assessment`: one result for each assessed parameter, including an error value and a score.
- `overall_score`: the final weighted score from 0 to 100.

The response shape is demonstrated in `examples/backend_ex_prob_response.json` and formally defined by the `AssessmentResponse` schema in `openapi.yaml`.

The meaning of each `error` value depends on the parameter. See `SCORING_SYSTEM.md`. An error is not itself a score.

## 6. Units and conventions

Version 1 conventions:

| Parameter | Convention |
|---|---|
| Length coordinates and dimensions | millimetres (mm) |
| Surface area | square millimetres (mm²) |
| Volume | cubic millimetres (mm³) |
| Center of mass | `[x, y, z]`, in mm, in the question's declared model coordinate frame |
| Bounding box | `[x, y, z]` dimensions, in mm, in the question's declared axis order |
| Body, face, edge counts | Non-negative integers |
| Face types | Object mapping surface-type names to non-negative integer counts |

The question definition must identify the coordinate frame and axis orientation used by its expected values. The frontend and backend must use the same convention.

## 7. Face-type naming

Use consistent lowercase keys. The initial supported names are:
- `plane`
- `cylinder`
- `cone`
- `sphere`
- `torus`
- `other`

The backend must define how unsupported or freeform surface types are categorized. Do not use visual descriptions such as `smooth` as a geometric surface type.

Face and edge counts can depend on CAD-kernel topology and modeling operations. They should be treated as assessment criteria with documented tolerances, not as universal proof that two models are identical.

## 8. Errors and HTTP status codes

The API should return a consistent JSON error object with:
- `error_code`: stable machine-readable identifier;
- `message`: short human-readable explanation;
- `details`: optional field-level validation information.

Expected statuses:
- `200`: assessment completed.
- `400`: malformed request or invalid request content.
- `404`: question ID does not exist.
- `422`: structurally valid JSON that fails schema or semantic validation, if the backend framework uses this status.
- `500`: unexpected server error.

The backend should not expose stack traces, secrets, or internal implementation details to the frontend.

## 9. Scope and limitations

- Version 1 uses manually entered model parameters.
- The backend can assess the submitted values, but cannot prove the user created the model unless a CAD-file upload and parsing feature is added.
- User accounts, authentication, persistent attempt history, and history endpoints are not fully specified in this Version 1 contract. Do not invent those APIs; propose them as a separate contract change.
- Question retrieval endpoints may be added when the question-bank implementation is designed. The initial agreed endpoint in this draft is assessment submission.

## 10. Change process

Any change to a public API field, type, endpoint, status code, unit, coordinate convention, or scoring meaning must:
1. Be proposed with the reason for the change.
2. Identify frontend and backend impact.
3. Update `openapi.yaml`, this document, relevant examples, and scoring documentation as needed.
4. Be reviewed and approved by the project lead.
5. Be merged with compatible frontend/backend changes or a documented migration plan.
