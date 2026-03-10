from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.scan_execution import ScanExecution, ScanExecutionStatus
from app.services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}


@celery_app.task(name="app.workers.tasks.run_scan_execution")
def run_scan_execution(scan_execution_id: int) -> dict[str, int | str]:
    """
    Phase 3 worker:
    Starts execution, discovers topic candidates and persists them.
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

        discovery_summary = DiscoveryService(db).discover_and_persist(scan_execution_id=scan_execution_id)
        scan_execution = db.get(ScanExecution, scan_execution_id)
        if scan_execution is None:
            logger.warning("scan_execution_lost_after_discovery", extra={"scan_execution_id": scan_execution_id})
            return {"status": "not_found_after_discovery", "scan_execution_id": scan_execution_id}

        scan_execution.discovered_links_count = discovery_summary.discovered_links_count
        scan_execution.valid_topics_count = discovery_summary.valid_topics_count
        scan_execution.status = ScanExecutionStatus.completed
        scan_execution.finished_at = datetime.now(timezone.utc)
        db.add(scan_execution)
        db.commit()

        return {
            "status": "completed",
            "scan_execution_id": scan_execution_id,
            "discovered_links_count": discovery_summary.discovered_links_count,
            "valid_topics_count": discovery_summary.valid_topics_count,
            "persisted_topics_count": discovery_summary.persisted_topics_count,
        }
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
