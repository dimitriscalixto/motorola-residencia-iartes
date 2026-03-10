from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse


class LinkType(str, Enum):
    topic = "topic"
    listing = "listing"
    irrelevant = "irrelevant"


@dataclass(frozen=True)
class ClassifiedLink:
    original_url: str
    normalized_url: str
    link_type: LinkType
    reason: str


TRACKING_QUERY_PARAMS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
    "source",
}

IRRELEVANT_PATH_KEYWORDS = (
    "/help",
    "/faq",
    "/login",
    "/signin",
    "/register",
    "/profile",
    "/user",
    "/account",
    "/messages",
    "/notifications",
    "/terms",
    "/privacy",
    "/search",
)

TOPIC_PATTERNS = (
    re.compile(r"/m-p/\d+", re.IGNORECASE),
    re.compile(r"/td-p/\d+", re.IGNORECASE),
)

LISTING_PATTERNS = (
    re.compile(r"/ct-p/motorolacommunity", re.IGNORECASE),
    re.compile(r"/bd-p/motorolacommunity", re.IGNORECASE),
    re.compile(r"/motorola-community/page/\d+", re.IGNORECASE),
)


class LinkClassifier:
    def __init__(
        self,
        base_url: str = "https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity",
        allowed_host: str = "forums.lenovo.com",
    ):
        self.base_url = base_url
        self.allowed_host = allowed_host

    def normalize_url(self, url: str) -> str:
        if not url:
            return ""

        candidate = url.strip()
        if not candidate:
            return ""

        # Resolve relative Lenovo forum URLs against the fixed Motorola source URL.
        if candidate.startswith("/"):
            candidate = urljoin(self.base_url, candidate)

        parsed = urlparse(candidate)
        if not parsed.scheme and not parsed.netloc:
            candidate = urljoin(self.base_url, candidate)
            parsed = urlparse(candidate)

        if parsed.scheme not in {"http", "https"}:
            return ""

        filtered_query_items: list[tuple[str, str]] = []
        for key, value in parse_qsl(parsed.query, keep_blank_values=True):
            key_lower = key.lower()
            if key_lower.startswith("utm_") or key_lower in TRACKING_QUERY_PARAMS:
                continue
            filtered_query_items.append((key, value))

        normalized_query = urlencode(filtered_query_items, doseq=True)
        normalized_path = parsed.path.rstrip("/") if parsed.path != "/" else parsed.path

        return urlunparse(
            (
                "https",
                parsed.netloc.lower(),
                normalized_path,
                "",
                normalized_query,
                "",
            )
        )

    def classify(self, url: str) -> ClassifiedLink:
        normalized_url = self.normalize_url(url)
        if not normalized_url:
            return ClassifiedLink(url, normalized_url, LinkType.irrelevant, "invalid_or_unsupported_url")

        parsed = urlparse(normalized_url)
        path_lower = parsed.path.lower()

        if parsed.netloc != self.allowed_host:
            return ClassifiedLink(url, normalized_url, LinkType.irrelevant, "external_host")

        if any(keyword in path_lower for keyword in IRRELEVANT_PATH_KEYWORDS):
            return ClassifiedLink(url, normalized_url, LinkType.irrelevant, "blocked_path_keyword")

        if any(pattern.search(path_lower) for pattern in TOPIC_PATTERNS):
            return ClassifiedLink(url, normalized_url, LinkType.topic, "topic_pattern_match")

        if any(pattern.search(path_lower) for pattern in LISTING_PATTERNS):
            return ClassifiedLink(url, normalized_url, LinkType.listing, "listing_pattern_match")

        if "page=" in parsed.query.lower():
            return ClassifiedLink(url, normalized_url, LinkType.listing, "listing_query_pagination")

        return ClassifiedLink(url, normalized_url, LinkType.irrelevant, "unmatched_internal_url")

