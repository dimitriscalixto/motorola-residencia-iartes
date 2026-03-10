from app.services.link_classifier import LinkClassifier, LinkType


def test_classifies_topic_url() -> None:
    classifier = LinkClassifier()
    result = classifier.classify("https://forums.lenovo.com/t5/Motorola-Community/Camera-bug/m-p/543210")

    assert result.link_type == LinkType.topic
    assert result.normalized_url.endswith("/m-p/543210")


def test_classifies_listing_url_with_pagination_query() -> None:
    classifier = LinkClassifier()
    result = classifier.classify(
        "https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity?page=2&utm_source=test"
    )

    assert result.link_type == LinkType.listing
    assert "utm_source" not in result.normalized_url
    assert "page=2" in result.normalized_url


def test_classifies_external_url_as_irrelevant() -> None:
    classifier = LinkClassifier()
    result = classifier.classify("https://example.com/some-page")

    assert result.link_type == LinkType.irrelevant
    assert result.reason == "external_host"

