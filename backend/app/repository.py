import logging
from typing import Protocol

from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.errors import QuestionConfigError, QuestionNotFound, sanitize_errors
from app.models import Base, QuestionRow
from app.questions import QuestionConfig, load_seed_questions

logger = logging.getLogger(__name__)


class QuestionRepository(Protocol):
    def get(self, question_id: str) -> QuestionConfig:
        """Return the question, or raise QuestionNotFound."""


class InMemoryQuestionRepository:
    def __init__(self, questions: list[QuestionConfig]) -> None:
        self._questions = {question.question_id: question for question in questions}

    def get(self, question_id: str) -> QuestionConfig:
        try:
            return self._questions[question_id]
        except KeyError as exc:
            raise QuestionNotFound(question_id) from exc


class SqlAlchemyQuestionRepository:
    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

    def init(self) -> None:
        Base.metadata.create_all(self.engine)
        questions = load_seed_questions()
        with self.session_factory() as session:
            inserted = _insert_missing(session, questions)
            session.commit()
        logger.info("Question seed inserted %s new question(s).", inserted)

    def get(self, question_id: str) -> QuestionConfig:
        with self.session_factory() as session:
            row = session.get(QuestionRow, question_id)
            if row is None:
                raise QuestionNotFound(question_id)
            payload = {
                "question_id": row.question_id,
                "title": row.title,
                "coordinate_frame": row.coordinate_frame,
                "axis_order": row.axis_order,
                "criteria": row.criteria,
            }
        try:
            return QuestionConfig.model_validate(payload)
        except ValidationError as exc:
            raise QuestionConfigError(
                "Question configuration is invalid.",
                details=sanitize_errors(exc.errors()),
            ) from exc


def _insert_missing(session: Session, questions: list[QuestionConfig]) -> int:
    """Insert seed questions that are not already stored.

    Existing rows are left unchanged so a later edit in the database is not
    overwritten when the server starts.
    """
    existing_ids = set(session.scalars(select(QuestionRow.question_id)))
    inserted = 0
    for question in questions:
        if question.question_id in existing_ids:
            continue
        session.add(
            QuestionRow(
                question_id=question.question_id,
                title=question.title,
                coordinate_frame=question.coordinate_frame,
                axis_order=question.axis_order,
                criteria=question.criteria.model_dump(mode="json"),
            )
        )
        inserted += 1
    return inserted
