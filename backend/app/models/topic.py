import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TopicProcessingStatus(str, enum.Enum):
    discovery_queued = "discovery_queued"
    discovering_links = "discovering_links"
    links_discovered = "links_discovered"
    scraping_topic = "scraping_topic"
    extracting_fields = "extracting_fields"
    generating_tests = "generating_tests"
    completed = "completed"
    failed = "failed"


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_execution_id: Mapped[int] = mapped_column(
        ForeignKey("scan_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)

    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    complaint_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    complaint_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_model_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    source_listing_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    discovered_from_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    discovery_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    crawl_depth: Mapped[int | None] = mapped_column(Integer, nullable=True)

    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    processing_status: Mapped[TopicProcessingStatus] = mapped_column(
        Enum(TopicProcessingStatus, name="topic_processing_status"),
        nullable=False,
        default=TopicProcessingStatus.discovery_queued,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    scan_execution = relationship("ScanExecution", back_populates="topics")
    test_cases = relationship("TestCase", back_populates="topic", cascade="all, delete-orphan")

