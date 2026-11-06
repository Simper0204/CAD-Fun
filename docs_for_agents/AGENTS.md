# CAD Fun — Instructions for AI Coding Agents

These instructions apply to every AI coding agent working in this repository.

## 1. Read the project contract before coding

Before creating, editing, or refactoring project code, read all six project documents:

1. `docs_for_agents/API_CONTRACT.md`
2. `docs_for_agents/openapi.yaml`
3. `docs_for_agents/SCORING_SYSTEM.md`
4. `docs_for_agents/examples/frontend_ex_prob_submit.json`
5. `docs_for_agents/examples/backend_ex_prob_response.json`
6. `README.md` (repository root)

Do not rely on an example alone. The OpenAPI specification is authoritative for API structure; the scoring document is authoritative for scoring rules; the API contract explains the intended integration. Examples illustrate those rules.

If one document conflicts with another, do not guess. Report the conflict to the project lead. Until it is resolved:
- `openapi.yaml` governs endpoint names, HTTP methods, request/response schemas, and field names.
- `SCORING_SYSTEM.md` governs scoring formulas and parameter comparison.
- `API_CONTRACT.md` governs agreed integration behavior not represented in OpenAPI.
- Example JSON files are illustrative and must not override the specifications.

## 2. Project overview

CAD Fun is a learning website for CAD beginners. Users solve CAD exercises in external CAD software, submit model parameters, and receive an assessment.

Version 1 uses manually entered parameters. Do not claim that the website has verified the actual CAD file or model unless file upload and model parsing are implemented.

## 3. API compatibility rules

- Implement the API defined in `docs/openapi.yaml`.
- Do not independently rename, remove, or add public API fields.
- Do not change endpoint paths, HTTP methods, status codes, required fields, or data types without approval from the project lead.
- Use JSON request and response bodies with `Content-Type: application/json`.
- Follow the documented units, axis order, coordinate frame, and validation rules.
- Do not return undocumented fields that the frontend must depend on.
- Do not make the frontend reproduce the backend's scoring calculations.

## 4. Frontend rules

- Call the backend through the documented API endpoints.
- Keep HTTP/API calls in a dedicated service or API-client layer rather than scattering them across UI components.
- Validate user input for usability, but treat backend validation as authoritative.
- Handle loading, successful responses, validation errors, not-found responses, and server errors.
- Display the values returned by the backend; do not invent scores or infer missing scores.
- Use the exact field names and types from OpenAPI.

## 5. Backend rules

- Implement and validate the request schema defined in OpenAPI.
- Keep route handling, input validation, assessment logic, and persistence separated where practical.
- Return the documented response schema and appropriate HTTP status codes.
- Never trust client-submitted scores. The client submits model parameters; the backend calculates assessment results.
- Use the rules in `SCORING_SYSTEM.md`. Do not invent tolerances, weights, or parameter conventions.
- Treat missing or invalid values as validation errors rather than silently substituting arbitrary defaults.

## 6. Unresolved decisions

The current project specification deliberately flags some decisions as unresolved, especially the exact definition and representation of moment of inertia.

If an unresolved decision affects your task:
1. Do not make an undocumented assumption.
2. Explain the decision that is needed and the available options.
3. Propose a recommendation with its consequences.
4. Wait for the project lead to approve the decision before implementing that part.

Do not change the shared contract as a side effect of implementing a feature.

## 7. Collaboration and Git rules

- Work only in your assigned area unless the project lead approves broader changes.
- Do not overwrite or revert another developer's work.
- Do not edit shared API documents independently.
- If a contract change is necessary, propose it separately and explain why both frontend and backend need it.
- Keep changes focused and explain files changed in the pull request.
- Run relevant tests and report what was and was not tested.
- Do not claim integration works unless the frontend and backend have actually been tested together.

## 8. Required completion report

When finishing a task, report:
- What you implemented.
- Which files you changed.
- Which API endpoints or schemas you used.
- Tests run and their results.
- Any assumptions, unresolved questions, or deviations from the contract.

If you discover a mismatch between implementation and documentation, stop and report it rather than silently choosing one.

The project uses the following standardized technology stack:

- Frontend: React + TypeScript + Vite
- Styling: Tailwind CSS
- Backend: Python + FastAPI
- Data validation: Pydantic
- Database: PostgreSQL
- Database ORM: SQLAlchemy
- API communication: REST + JSON
- API specification: OpenAPI

All developers and AI coding agents must use these technologies unless the project lead explicitly approves a change.

Do not introduce alternative frameworks, programming languages, databases, or major dependencies without approval.

Frontend and backend implementations must follow the shared API contract.