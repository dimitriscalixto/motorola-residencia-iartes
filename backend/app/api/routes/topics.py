from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_topics() -> dict:
    return {"items": [], "total": 0}

