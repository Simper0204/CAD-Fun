import os

import pytest
from sqlalchemy import create_engine, text

from app.repository import SqlAlchemyQuestionRepository

pytestmark = pytest.mark.skipif(
    not os.getenv("CADFUN_TEST_DATABASE_URL"),
    reason="Set CADFUN_TEST_DATABASE_URL to a disposable PostgreSQL database to run this test.",
)


def test_seed_is_inserted_once_and_can_be_read_back() -> None:
    database_url = os.environ["CADFUN_TEST_DATABASE_URL"]
    repository = SqlAlchemyQuestionRepository(database_url)
    repository.init()
    repository.init()

    question = repository.get("CAD001")
    assert question.criteria.volume.expected == 125.5

    engine = create_engine(database_url)
    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM questions WHERE question_id = 'CAD001'")
        ).scalar_one()
    assert count == 1
