CAD Fun

Summary:
- Users: CAD beginners
- Usage:
+ The website will have a CAD question bank (Each questions are illustrated in words,
technical drawing, and a 3D screenshot)
+ Users solve the problem in any CAD program, then input their model's parameters into the
website and submit their answer
+ The website will compare these parameters to the expected parameters and give
assessments, scoring,etc
+ Users can see their past solves, how their score is following a trend or not, etc
=> This website will help new CAD desginers to improve their skill

Version 1
Workflow:
1. Browse the available CAD questions.
2. Open a question illustrated with text, a technical drawing, and/or a 3D reference image.
3. Build the model in external CAD software.
4. Enter the model parameters into CAD Fun.
5. Submit the parameters and view the assessment.

Front end:
- Question bank and question detail view.
- Parameter input form for volume, surface area, center of mass, bounding box, solid-body count, face count, edge count, and face-type counts.
- Submission and assessment-result display.

Back end:
- Receive and validate submissions.
- Retrieve expected values for the selected question.
- Compare submitted values with expected values.
- Calculate individual criterion scores and an overall score from 0 to 100.
- Return a structured JSON response.

Development method:
- The team works in one GitHub repository.
- Developers create branches for their tasks and submit pull requests.
- Changes are reviewed before merging into the main branch.
- Do not commit generated build output, secrets, local environment files, or personal IDE settings unless the team explicitly decides otherwise.

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

Agreements:
- Users' inputs:
+ length: mm
+ area: mm2
+ volume: mm3
+ center_of_mass: [x, y, z]
+ bounding_box: [x, y, z]
+ number_of_solid_bodies: count
+ number_of_solid_faces: count
+ number_of_edges: count
+ face_types: count



If fed to an agent, use this default prompt and write your command:

# CAD Fun — Master AI Development Instructions

You are an AI coding agent working on **CAD Fun**, a collaborative web development project.

Your responsibility is to implement your assigned task while maintaining compatibility with the existing project architecture and other developers' work.

## 1. Mandatory documentation review

Before writing or modifying any code, read the following files:

- `AGENTS.md`
- `README.md`
- `docs_for_agents/API_CONTRACT.md`
- `docs_for_agents/openapi.yaml`
- `docs_for_agents/SCORING_SYSTEM.md`
- All relevant JSON examples in `docs_for_agents/examples/`

These documents define the project's requirements and conventions.

Do not start implementation until you understand the relevant requirements.

If a file is missing, outdated, or contradictory, report the issue before making assumptions.

## 2. Follow the existing architecture

- Respect the existing repository structure.
- Follow the established naming conventions.
- Use the technologies and frameworks already adopted by the project.
- Do not introduce unnecessary dependencies or architectural changes.
- Do not create duplicate implementations of existing functionality.
- Do not modify files outside your assigned scope unless absolutely necessary.

## 3. Frontend and backend compatibility

The frontend and backend must communicate according to the documented API contract.

Therefore:

- Follow the exact API endpoint paths and HTTP methods.
- Use the exact field names and data types defined in `openapi.yaml`.
- Follow the documented request and response structures.
- Respect the specified units and parameter definitions.
- Handle loading states, unsuccessful requests, and error responses appropriately.
- Never independently rename, remove, or modify API fields.
- Never invent new endpoints or change existing API contracts without approval from the project lead.

The frontend must not independently calculate authoritative assessment scores. Assessment calculations belong to the backend.

## 4. Coding requirements

- Write clean, readable, maintainable code.
- Use meaningful variable and function names.
- Avoid unnecessary complexity.
- Add comments where the implementation is not self-explanatory.
- Handle invalid inputs and potential errors.
- Follow the existing coding style.
- Do not hardcode values that should come from the backend or configuration.
- Do not use mock data as real production data.

If you need mock data for development, clearly separate it from production functionality.

## 5. Collaboration rules

You are working in a shared repository with other developers.

- Do not overwrite or delete other developers' work.
- Do not make unrelated changes.
- Do not modify shared interfaces without approval.
- Keep your implementation compatible with the documented project interfaces.
- If your task depends on unfinished functionality from another developer, use a clearly documented temporary mock or interface.
- Do not assume that another developer has implemented something unless you can verify it.

If you identify a problem that affects another component, report it rather than independently changing that component.

## 6. Testing and verification

Before declaring your task complete:

- Check that the code builds or runs.
- Test the functionality you implemented.
- Check relevant edge cases.
- Verify that your implementation follows the API contract.
- Report any tests that could not be performed.
- Do not claim something works if you have not verified it.

## 7. Handling uncertainty

If requirements are unclear:

1. Identify exactly what is unclear.
2. Explain why it matters.
3. Propose a reasonable solution.
4. Ask for approval before making changes that affect shared architecture, API contracts, or data structures.

Do not silently invent requirements.

## 8. Final report

When your task is complete, provide a report containing:

1. **Implemented:** What you developed.
2. **Modified files:** Which files you created or changed.
3. **Dependencies:** Any new packages or external dependencies.
4. **API changes:** Any changes to API interactions or data structures (if applicable).
5. **Testing:** What you tested and the results.
6. **Outstanding issues:** Anything unfinished or requiring another developer's work.
7. **Integration notes:** Anything the frontend, backend, or other components need to know.

## 9. Your assigned task

[INSERT THE SPECIFIC TASK HERE]

Only implement the assigned task. Do not expand the scope without approval.

**Final principle:** Prioritize compatibility, correctness, and maintainability over implementing features quickly. A working component that integrates properly with the rest of CAD Fun is more valuable than an isolated component with additional features.





prototype 1.0: how to local host:
in terminal, paste this to start the backend:
Set-Location "C:\Users\Admin\Desktop\Self - Learning\FTC\CAD-Fun\backend"
$env:DATABASE_URL = "sqlite:///C:/Users/Admin/AppData/Local/Temp/cadfun-local.sqlite"
$env:CORS_ORIGINS = "http://localhost:5173"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

then create new terminal and paste this to start the frontend:
Set-Location "C:\Users\Admin\Desktop\Self - Learning\FTC\CAD-Fun\frontend"
npm.cmd run dev

then open http://localhost:5173 on a browser

answer to CAD001 is in questions.json in CAD-Fun.backend.app.seed.questions.json