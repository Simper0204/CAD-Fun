from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class QuestionRow(Base):
    __tablename__ = "questions"

    question_id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    coordinate_frame: Mapped[str] = mapped_column(Text, nullable=False)
    axis_order: Mapped[str] = mapped_column(Text, nullable=False)
    criteria: Mapped[dict] = mapped_column(JSONB, nullable=False)
