import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ScanExecutionStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ScanExecution(Base):
    __tablename__ = "scan_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False, default="lenovo_motorola_community")
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[ScanExecutionStatus] = mapped_column(
        Enum(ScanExecutionStatus, name="scan_execution_status"),
        nullable=False,
        default=ScanExecutionStatus.queued,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    discovered_links_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_topics_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_topics_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_topics_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    topics = relationship("Topic", back_populates="scan_execution", cascade="all, delete-orphan")

