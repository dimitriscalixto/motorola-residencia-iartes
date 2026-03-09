from app.db.base import Base
from app.db.session import engine
from app.models import scan_execution, test_case, topic  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

