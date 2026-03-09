class FirecrawlClient:
    """
    Phase 1 scaffold.
    Phase 4 will contain specialized methods for Lenovo Motorola forum crawling.
    """

    def discover_motorola_topics(self) -> list[dict]:
        raise NotImplementedError("Firecrawl integration will be implemented in Phase 4")

    def scrape_topic(self, _: str) -> dict:
        raise NotImplementedError("Firecrawl integration will be implemented in Phase 4")

