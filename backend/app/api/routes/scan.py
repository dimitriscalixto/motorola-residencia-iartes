from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.scan_execution import ScanExecutionStatus
from app.schemas.scan import ScanExecutionRead, ScanStartResponse
from app.services.scan_service import ScanService

router = APIRouter()


@router.post("/start", response_model=ScanStartResponse, status_code=status.HTTP_202_ACCEPTED)
def start_scan(db: Session = Depends(get_db)) -> ScanStartResponse:
    service = ScanService(db)
    scan_execution = service.start_scan()
    if scan_execution.status == ScanExecutionStatus.failed:
        message = "Scan execution created but queue dispatch failed"
    else:
        message = "Scan execution started from fixed Motorola community source"
    return ScanStartResponse(
        message=message,
        scan_execution=ScanExecutionRead.model_validate(scan_execution),
    )


@router.get("/latest", response_model=ScanExecutionRead | None)
def get_latest_scan(db: Session = Depends(get_db)) -> ScanExecutionRead | None:
    service = ScanService(db)
    latest_scan = service.get_latest_scan()
    if latest_scan is None:
        return None
    return ScanExecutionRead.model_validate(latest_scan)
