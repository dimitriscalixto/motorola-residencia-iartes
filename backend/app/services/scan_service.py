from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.models.scan_execution import ScanExecution, ScanExecutionStatus

logger = logging.getLogger(__name__)
settings = get_settings()


class ScanService:
    """Coordinates scan execution lifecycle for Phase 2."""

    def __init__(self, db: Session):
        self.db = db

    def start_scan(self) -> ScanExecution:
        scan_execution = ScanExecution(
            source_name="lenovo_motorola_community",
            source_url=str(settings.motorola_community_url),
            status=ScanExecutionStatus.queued,
        )
        self.db.add(scan_execution)
        self.db.commit()
        self.db.refresh(scan_execution)

        try:
            celery_app.send_task("app.workers.tasks.run_scan_execution", args=[scan_execution.id])
            logger.info("scan_execution_enqueued", extra={"scan_execution_id": scan_execution.id})
        except Exception as exc:
            logger.exception(
                "scan_execution_enqueue_failed",
                extra={"scan_execution_id": scan_execution.id, "error_type": type(exc).__name__},
            )
            scan_execution.status = ScanExecutionStatus.failed
            scan_execution.finished_at = datetime.now(timezone.utc)
            self.db.add(scan_execution)
            self.db.commit()
            self.db.refresh(scan_execution)

        return scan_execution

    def get_latest_scan(self) -> ScanExecution | None:
        statement = select(ScanExecution).order_by(ScanExecution.created_at.desc()).limit(1)
        return self.db.scalar(statement)
