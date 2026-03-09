import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Category(str, enum.Enum):
    crash = "crash"
    performance = "performance"
    battery = "battery"
    camera = "camera"
    connectivity = "connectivity"
    display = "display"
    audio = "audio"
    charging = "charging"
    ui_ux = "ui_ux"
    update = "update"
    notification = "notification"
    app_compatibility = "app_compatibility"
    security = "security"
    other = "other"


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    preconditions_json: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    steps_json: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity, name="test_case_severity"), nullable=False)
    category: Mapped[Category] = mapped_column(Enum(Category, name="test_case_category"), nullable=False)
    device_model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_complaint_summary: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    topic = relationship("Topic", back_populates="test_cases")

