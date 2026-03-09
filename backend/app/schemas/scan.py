from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.scan_execution import ScanExecutionStatus


class ScanExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    source_url: str
    status: ScanExecutionStatus
    started_at: datetime | None
    finished_at: datetime | None
    discovered_links_count: int
    valid_topics_count: int
    processed_topics_count: int
    failed_topics_count: int
    created_at: datetime
    updated_at: datetime


class ScanStartResponse(BaseModel):
    message: str
    scan_execution: ScanExecutionRead

