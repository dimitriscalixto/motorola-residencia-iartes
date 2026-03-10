from __future__ import annotations

import logging
import re
from collections import deque
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, urlunparse

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

HREF_PATTERN = re.compile(r"""href=["']([^"']+)["']""", re.IGNORECASE)
LISTING_PATH_HINTS = ("/ct-p/motorolacommunity", "/bd-p/motorolacommunity", "/motorola-community/page/")


@dataclass(frozen=True)
class DiscoveredLink:
    url: str
    discovered_from_url: str | None
    source_listing_url: str | None
    discovery_method: str
    crawl_depth: int


class FirecrawlClient:
    """
    Domain-specialized discovery client for Lenovo Motorola Community.
    """

    def __init__(self, http_client: httpx.Client | None = None):
        self.firecrawl_base_url = str(settings.firecrawl_base_url).rstrip("/")
        self.firecrawl_api_key = settings.firecrawl_api_key
        self.start_url = str(settings.motorola_community_url)
        self.allowed_host = urlparse(self.start_url).netloc.lower()
        self.http_client = http_client or httpx.Client(timeout=20.0, follow_redirects=True)

    def discover_motorola_topics(self, max_listing_pages: int = 8, max_depth: int = 2) -> list[DiscoveredLink]:
        firecrawl_results = self._discover_via_firecrawl_map(limit=max_listing_pages * 120)
        if firecrawl_results:
            return firecrawl_results

        logger.info("firecrawl_map_unavailable_using_http_fallback")
        return self._discover_via_http(max_listing_pages=max_listing_pages, max_depth=max_depth)

    def scrape_topic(self, _: str) -> dict:
        raise NotImplementedError("Detailed topic scraping will be implemented in Phase 4")

    def _discover_via_firecrawl_map(self, limit: int) -> list[DiscoveredLink]:
        if not self.firecrawl_api_key or self.firecrawl_api_key == "changeme":
            return []

        headers = {
            "Authorization": f"Bearer {self.firecrawl_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "url": self.start_url,
            "limit": limit,
            "includeSubdomains": False,
        }

        try:
            response = self.http_client.post(f"{self.firecrawl_base_url}/v1/map", headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
        except Exception as exc:
            logger.warning("firecrawl_map_failed", extra={"error_type": type(exc).__name__})
            return []

        raw_links: list[str] = []
        if isinstance(body, dict):
            if isinstance(body.get("links"), list):
                raw_links = [link for link in body["links"] if isinstance(link, str)]
            elif isinstance(body.get("data"), list):
                raw_links = [link for link in body["data"] if isinstance(link, str)]
            elif isinstance(body.get("data"), dict) and isinstance(body["data"].get("links"), list):
                raw_links = [link for link in body["data"]["links"] if isinstance(link, str)]

        results: list[DiscoveredLink] = []
        for link in raw_links:
            normalized = self._normalize_url(link)
            if not normalized:
                continue
            results.append(
                DiscoveredLink(
                    url=normalized,
                    discovered_from_url=self.start_url,
                    source_listing_url=self.start_url,
                    discovery_method="firecrawl_map",
                    crawl_depth=1,
                )
            )
        return results

    def _discover_via_http(self, max_listing_pages: int, max_depth: int) -> list[DiscoveredLink]:
        queue: deque[tuple[str, str | None, int]] = deque([(self.start_url, None, 0)])
        visited_listing_urls: set[str] = set()
        discovered_links: list[DiscoveredLink] = []

        while queue and len(visited_listing_urls) < max_listing_pages:
            current_url, parent_url, depth = queue.popleft()
            normalized_current = self._normalize_url(current_url)
            if not normalized_current or normalized_current in visited_listing_urls:
                continue

            visited_listing_urls.add(normalized_current)
            html_content = self._fetch_html(normalized_current)
            if not html_content:
                continue

            discovery_method = "http_listing_seed" if depth == 0 else "http_listing_pagination"
            discovered_links.append(
                DiscoveredLink(
                    url=normalized_current,
                    discovered_from_url=parent_url,
                    source_listing_url=parent_url or normalized_current,
                    discovery_method=discovery_method,
                    crawl_depth=depth,
                )
            )

            for href in self._extract_links(html_content, normalized_current):
                normalized_href = self._normalize_url(href)
                if not normalized_href:
                    continue

                discovered_links.append(
                    DiscoveredLink(
                        url=normalized_href,
                        discovered_from_url=normalized_current,
                        source_listing_url=normalized_current,
                        discovery_method="http_extract",
                        crawl_depth=depth + 1,
                    )
                )

                if depth + 1 <= max_depth and self._looks_like_listing_url(normalized_href):
                    queue.append((normalized_href, normalized_current, depth + 1))

        return discovered_links

    def _fetch_html(self, url: str) -> str:
        for _ in range(3):
            try:
                response = self.http_client.get(url)
                response.raise_for_status()
                return response.text
            except Exception as exc:
                logger.warning("listing_fetch_failed", extra={"url": url, "error_type": type(exc).__name__})
        return ""

    def _extract_links(self, html: str, base_url: str) -> list[str]:
        links: list[str] = []
        for href in HREF_PATTERN.findall(html):
            if href.startswith("#") or href.lower().startswith("javascript:") or href.lower().startswith("mailto:"):
                continue
            resolved = urljoin(base_url, href)
            parsed = urlparse(resolved)
            if parsed.netloc.lower() != self.allowed_host:
                continue
            links.append(resolved)
        return links

    def _looks_like_listing_url(self, url: str) -> bool:
        parsed = urlparse(url)
        path_lower = parsed.path.lower()
        return any(hint in path_lower for hint in LISTING_PATH_HINTS) or "page=" in parsed.query.lower()

    def _normalize_url(self, url: str) -> str:
        candidate = urljoin(self.start_url, url)
        parsed = urlparse(candidate)
        if parsed.scheme not in {"http", "https"}:
            return ""
        if parsed.netloc.lower() != self.allowed_host:
            return ""
        path = parsed.path.rstrip("/") if parsed.path != "/" else parsed.path
        return urlunparse(("https", parsed.netloc.lower(), path, "", parsed.query, ""))
