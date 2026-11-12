import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.assessments import router
from app.config import get_settings
from app.errors import APIError, sanitize_errors
from app.repository import QuestionRepository, SqlAlchemyQuestionRepository

logger = logging.getLogger(__name__)

JSON_ERROR_TYPES = {"json_invalid", "json_decode"}


def create_app(repository: QuestionRepository | None = None) -> FastAPI:
    settings = get_settings()
    owns_database = repository is None
    if repository is None:
        repository = SqlAlchemyQuestionRepository(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if owns_database:
            repository.init()
        yield

    app = FastAPI(
        title="CAD Fun API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.questions = repository
    _register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )
    return app


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def handle_api_error(_request: Request, exc: APIError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("API error %s: %s", exc.error_code, exc.message)
        return JSONResponse(status_code=exc.status_code, content=exc.to_body())

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = sanitize_errors(exc.errors())
        if any(detail["type"] in JSON_ERROR_TYPES for detail in details):
            return JSONResponse(
                status_code=400,
                content={
                    "error_code": "MALFORMED_REQUEST",
                    "message": "Request body is not valid JSON.",
                    "details": details,
                },
            )
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": "Request failed validation.",
                "details": details,
            },
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_request: Request, exc: HTTPException) -> JSONResponse:
        codes = {
            400: "MALFORMED_REQUEST",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
        }
        message = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": codes.get(exc.status_code, "HTTP_ERROR"),
                "message": message,
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            },
        )


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
