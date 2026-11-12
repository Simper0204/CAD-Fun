# CAD Fun frontend

The frontend implements the Version 1 manual assessment flow and sends submissions to
`POST /api/v1/assessments`. It displays the response from the backend; scoring is not
calculated in the browser.

## Run locally

Start the backend first by following [`../backend/README.md`](../backend/README.md), then
in this directory run:

```powershell
npm ci
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`). The backend
must be running at `http://localhost:8000`.

To use a different backend, create a local `.env` file in this directory and set:

```text
VITE_API_BASE_URL=http://localhost:8000
```

The value is the backend base URL, without the `/api/v1/assessments` path. The default
already points at the documented local backend URL.

## Current Version 1 scope

- The backend currently seeds one provisional question, `CAD001`.
- The existing API contract defines assessment submission only; it does not provide
  question-list/detail retrieval, exercise instructions, or image URLs.
- Accordingly, the frontend submits to that one question and clearly identifies the
  missing question content instead of presenting invented instructions or artwork.
- User accounts, attempt history, and CAD-file upload/model verification are not part
  of the current contract.
