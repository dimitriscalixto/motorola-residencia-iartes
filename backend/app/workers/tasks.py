from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.scan_execution import ScanExecution, ScanExecutionStatus

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}


@celery_app.task(name="app.workers.tasks.run_scan_execution")
def run_scan_execution(scan_execution_id: int) -> dict[str, int | str]:
    """
    Phase 2 worker:
    Starts and finalizes execution lifecycle without discovery/scraping yet.
    """
    db = SessionLocal()
    try:
        scan_execution = db.get(ScanExecution, scan_execution_id)
        if scan_execution is None:
            logger.warning("scan_execution_not_found", extra={"scan_execution_id": scan_execution_id})
            return {"status": "not_found", "scan_execution_id": scan_execution_id}

        scan_execution.status = ScanExecutionStatus.running
        scan_execution.started_at = datetime.now(timezone.utc)
        db.add(scan_execution)
        db.commit()

        # Placeholder for Phase 3+ pipeline.
        scan_execution.status = ScanExecutionStatus.completed
        scan_execution.finished_at = datetime.now(timezone.utc)
        db.add(scan_execution)
        db.commit()

        return {"status": "completed", "scan_execution_id": scan_execution_id}
    except Exception:
        logger.exception("scan_execution_worker_failed", extra={"scan_execution_id": scan_execution_id})
        scan_execution = db.get(ScanExecution, scan_execution_id)
        if scan_execution is not None:
            scan_execution.status = ScanExecutionStatus.failed
            scan_execution.finished_at = datetime.now(timezone.utc)
            db.add(scan_execution)
            db.commit()
        raise
    finally:
        db.close()
