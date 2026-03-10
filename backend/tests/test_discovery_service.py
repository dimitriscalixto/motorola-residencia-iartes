import os
from datetime import datetime, timezone

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./phase2_test.db"

from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.integrations.firecrawl_client import DiscoveredLink  # noqa: E402
from app.models.scan_execution import ScanExecution, ScanExecutionStatus  # noqa: E402
from app.models.topic import Topic  # noqa: E402
from app.services.discovery_service import DiscoveryService  # noqa: E402


class FakeFirecrawlClient:
    def discover_motorola_topics(self, max_listing_pages: int = 8, max_depth: int = 2) -> list[DiscoveredLink]:
        return [
            DiscoveredLink(
                url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                discovered_from_url=None,
                source_listing_url=None,
                discovery_method="fake_seed",
                crawl_depth=0,
            ),
            DiscoveredLink(
                url="https://forums.lenovo.com/t5/Motorola-Community/Camera-bug/m-p/100001",
                discovered_from_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                source_listing_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                discovery_method="fake_extract",
                crawl_depth=1,
            ),
            DiscoveredLink(
                url="https://forums.lenovo.com/t5/Motorola-Community/Camera-bug/m-p/100001?utm_source=foo",
                discovered_from_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                source_listing_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                discovery_method="fake_extract",
                crawl_depth=1,
            ),
            DiscoveredLink(
                url="https://forums.lenovo.com/t5/Motorola-Community/Battery-drain/m-p/100002",
                discovered_from_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                source_listing_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                discovery_method="fake_extract",
                crawl_depth=1,
            ),
            DiscoveredLink(
                url="https://forums.lenovo.com/t5/login",
                discovered_from_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                source_listing_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                discovery_method="fake_extract",
                crawl_depth=1,
            ),
            DiscoveredLink(
                url="https://example.com/external-topic",
                discovered_from_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                source_listing_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
                discovery_method="fake_extract",
                crawl_depth=1,
            ),
        ]


def test_discovery_persists_deduplicated_topic_candidates() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        scan_execution = ScanExecution(
            source_name="lenovo_motorola_community",
            source_url="https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
            status=ScanExecutionStatus.running,
            started_at=datetime.now(timezone.utc),
        )
        db.add(scan_execution)
        db.commit()
        db.refresh(scan_execution)

        service = DiscoveryService(db=db, firecrawl_client=FakeFirecrawlClient())
        summary = service.discover_and_persist(scan_execution.id)

        topics = db.query(Topic).filter(Topic.scan_execution_id == scan_execution.id).all()
        db.refresh(scan_execution)

        assert summary.discovered_links_count == 3
        assert summary.listing_links_count == 1
        assert summary.valid_topics_count == 2
        assert summary.persisted_topics_count == 2
        assert len(topics) == 2
        assert scan_execution.discovered_links_count == 3
        assert scan_execution.valid_topics_count == 2

        second_summary = service.discover_and_persist(scan_execution.id)
        topics_after_second_run = db.query(Topic).filter(Topic.scan_execution_id == scan_execution.id).all()

        assert second_summary.persisted_topics_count == 0
        assert len(topics_after_second_run) == 2
    finally:
        db.query(Topic).delete()
        db.query(ScanExecution).delete()
        db.commit()
        db.close()

