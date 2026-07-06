from __future__ import annotations

from datetime import datetime
from pathlib import Path
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from ragops.config import get_settings


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"
    document_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    source_path: Mapped[str] = mapped_column(String, nullable=False)
    domain: Mapped[str] = mapped_column(String, default="technical_docs")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    versions: Mapped[list[DocumentVersion]] = relationship(back_populates="document")


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    version_id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.document_id"), nullable=False)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    valid_from: Mapped[str] = mapped_column(String, nullable=False)
    valid_to: Mapped[str | None] = mapped_column(String, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True)

    document: Mapped[Document] = relationship(back_populates="versions")
    chunks: Mapped[list[Chunk]] = relationship(back_populates="version")


class Chunk(Base):
    __tablename__ = "chunks"
    chunk_id: Mapped[str] = mapped_column(String, primary_key=True)
    version_id: Mapped[str] = mapped_column(ForeignKey("document_versions.version_id"), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    section_title: Mapped[str] = mapped_column(String, default="")
    start_char: Mapped[int] = mapped_column(Integer, default=0)
    end_char: Mapped[int] = mapped_column(Integer, default=0)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)

    version: Mapped[DocumentVersion] = relationship(back_populates="chunks")


class QueryRun(Base):
    __tablename__ = "queries"
    query_id: Mapped[str] = mapped_column(String, primary_key=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnswerRun(Base):
    __tablename__ = "answers"
    answer_id: Mapped[str] = mapped_column(String, primary_key=True)
    query_id: Mapped[str] = mapped_column(ForeignKey("queries.query_id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String, default="extractive-baseline")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RetrievalRun(Base):
    __tablename__ = "retrieval_runs"
    retrieval_run_id: Mapped[str] = mapped_column(String, primary_key=True)
    query_id: Mapped[str] = mapped_column(ForeignKey("queries.query_id"), nullable=False)
    retrieval_type: Mapped[str] = mapped_column(String, default="qdrant_hash_baseline")
    top_k: Mapped[int] = mapped_column(Integer, default=5)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)


class RetrievedChunk(Base):
    __tablename__ = "retrieved_chunks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    retrieval_run_id: Mapped[str] = mapped_column(ForeignKey("retrieval_runs.retrieval_run_id"), nullable=False)
    chunk_id: Mapped[str] = mapped_column(ForeignKey("chunks.chunk_id"), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    freshness_score: Mapped[float] = mapped_column(Float, default=1.0)


class FailureCase(Base):
    __tablename__ = "failure_cases"
    failure_id: Mapped[str] = mapped_column(String, primary_key=True)
    query_id: Mapped[str] = mapped_column(ForeignKey("queries.query_id"), nullable=False)
    answer_id: Mapped[str] = mapped_column(ForeignKey("answers.answer_id"), nullable=False)
    failure_code: Mapped[str] = mapped_column(String, nullable=False)
    root_component: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)


def _make_engine():
    settings = get_settings()
    if settings.database_url.startswith("sqlite"):
        Path("data").mkdir(exist_ok=True)
        return create_engine(settings.database_url, connect_args={"check_same_thread": False})
    return create_engine(settings.database_url)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_session():
    init_db()
    with SessionLocal() as session:
        yield session
