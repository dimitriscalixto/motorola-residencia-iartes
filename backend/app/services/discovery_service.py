from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.firecrawl_client import DiscoveredLink, FirecrawlClient
from app.models.scan_execution import ScanExecution
from app.models.topic import Topic, TopicProcessingStatus
from app.services.link_classifier import ClassifiedLink, LinkClassifier, LinkType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscoverySummary:
    discovered_links_count: int
    listing_links_count: int
    valid_topics_count: int
    persisted_topics_count: int


class DiscoveryService:
    def __init__(
        self,
        db: Session,
        firecrawl_client: FirecrawlClient | None = None,
        link_classifier: LinkClassifier | None = None,
    ):
        self.db = db
        self.firecrawl_client = firecrawl_client or FirecrawlClient()
        self.link_classifier = link_classifier or LinkClassifier()

    def discover_and_persist(self, scan_execution_id: int) -> DiscoverySummary:
        scan_execution = self.db.get(ScanExecution, scan_execution_id)
        if scan_execution is None:
            raise ValueError(f"scan_execution_not_found:{scan_execution_id}")

        discovered_links = self.firecrawl_client.discover_motorola_topics()
        relevant_links = self._classify_and_deduplicate(discovered_links)

        listing_links_count = sum(1 for _, classified, _ in relevant_links if classified.link_type == LinkType.listing)
        topic_links = [(normalized_url, classified, discovered) for normalized_url, classified, discovered in relevant_links if classified.link_type == LinkType.topic]

        persisted_topics_count = self._persist_topic_candidates(scan_execution_id=scan_execution.id, topic_links=topic_links)

        scan_execution.discovered_links_count = len(relevant_links)
        scan_execution.valid_topics_count = len(topic_links)
        self.db.add(scan_execution)
        self.db.commit()

        logger.info(
            "discovery_completed",
            extra={
                "scan_execution_id": scan_execution_id,
                "discovered_links_count": len(relevant_links),
                "listing_links_count": listing_links_count,
                "valid_topics_count": len(topic_links),
                "persisted_topics_count": persisted_topics_count,
            },
        )

        return DiscoverySummary(
            discovered_links_count=len(relevant_links),
            listing_links_count=listing_links_count,
            valid_topics_count=len(topic_links),
            persisted_topics_count=persisted_topics_count,
        )

    def _classify_and_deduplicate(
        self, discovered_links: list[DiscoveredLink]
    ) -> list[tuple[str, ClassifiedLink, DiscoveredLink]]:
        deduplicated: dict[str, tuple[ClassifiedLink, DiscoveredLink]] = {}

        for discovered in discovered_links:
            classified = self.link_classifier.classify(discovered.url)
            if classified.link_type == LinkType.irrelevant:
                continue

            key = classified.normalized_url
            if key not in deduplicated:
                deduplicated[key] = (classified, discovered)

        return [(normalized_url, classified, discovered) for normalized_url, (classified, discovered) in deduplicated.items()]

    def _persist_topic_candidates(
        self,
        scan_execution_id: int,
        topic_links: list[tuple[str, ClassifiedLink, DiscoveredLink]],
    ) -> int:
        existing_urls = set(
            self.db.scalars(select(Topic.url).where(Topic.scan_execution_id == scan_execution_id)).all()
        )
        persisted = 0

        for normalized_url, classified, discovered in topic_links:
            if normalized_url in existing_urls:
                continue

            topic = Topic(
                scan_execution_id=scan_execution_id,
                url=normalized_url,
                source_listing_url=discovered.source_listing_url,
                discovered_from_url=discovered.discovered_from_url,
                discovery_method=discovered.discovery_method,
                crawl_depth=discovered.crawl_depth,
                processing_status=TopicProcessingStatus.links_discovered,
                extracted_metadata_json={
                    "discovery_reason": classified.reason,
                    "original_discovered_url": discovered.url,
                },
            )
            self.db.add(topic)
            existing_urls.add(normalized_url)
            persisted += 1

        self.db.commit()
        return persisted

