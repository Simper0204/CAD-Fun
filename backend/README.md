# CAD Fun backend

Version 1 receives a CAD parameter submission, compares it with the expected values stored for that question, and returns an assessment.

The only public endpoint is:

`POST /api/v1/assessments`

Run it from this directory:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
docker compose up -d
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`docker compose up -d` starts the local PostgreSQL database described in `docker-compose.yml`. The defaults in `.env.example` match that database. Change them before any shared deployment.

Run the tests from this directory:

```powershell
pytest
```

The PostgreSQL round-trip test stays skipped until `CADFUN_TEST_DATABASE_URL` points at a disposable database.

## Question data

Expected values, comparison methods, tolerances, and weights live on each question row. The scorer does not hardcode them. On startup the app creates the `questions` table and inserts any seed question that is not already there. Restarting does not overwrite a row that was edited in the database.

To apply a changed seed for an existing question, delete that row and start the app again:

```sql
DELETE FROM questions WHERE question_id = 'CAD001';
```

`app/seed/questions.json` contains one provisional question, `CAD001`. Its expected values are the sample submission in `docs_for_agents/examples/frontend_ex_prob_submit.json`, so that submission scores 100. The sample response in the docs is illustrative and is not the result for this question. The project lead still needs to approve the tolerances and weights below.

| Criterion | Comparison | Tolerance | Weight |
|---|---|---|---|
| volume | percentage error | 5 percent | 1 |
| surface_area | percentage error | 5 percent | 1 |
| center_of_mass | maximum component, mm | 1 mm | 1 |
| bounding_box | maximum component, mm | 1 mm | 1 |
| number_of_solid_bodies | absolute count | 1 | 1 |
| number_of_solid_faces | absolute count | 2 | 1 |
| number_of_edges | absolute count | 2 | 1 |
| face_types | maximum count difference | 2 | 1 |

A count tolerance of 1 gives full points only for an exact integer match. Faces, edges, and face types use a tolerance of 2 so a difference of one count still receives partial points. A question can instead set `comparison` to `exact_match` for a count criterion.

If a scalar expected value is zero, that criterion must use `absolute` comparison. Percentage error is undefined in that case.

## Contract notes

- Unknown face-type names are rejected. The accepted names are `plane`, `cylinder`, `cone`, `sphere`, `torus`, and `other`.
- Negative volume, surface area, and bounding-box dimensions are rejected. Center-of-mass coordinates may be negative.
- Moment of inertia is not accepted or scored.
- Every criterion is returned in the assessment because the response schema requires it. A criterion with `enabled: false` is left out of `overall_score`.
- Displayed scores are rounded to two decimal places, half up. The overall score is calculated from the unrounded criterion scores.
- Question browsing, accounts, and attempt history are not part of this endpoint.
