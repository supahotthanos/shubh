"""Tests for mock providers — deterministic, no network."""
import asyncio

from app.providers.mock.authority import MockAuthorityProvider, MockWikipediaProvider
from app.providers.mock.gsc import MockGSCProvider
from app.providers.mock.llm import MockLLMProvider


def test_mock_llm_is_deterministic() -> None:
    async def run():
        provider = MockLLMProvider(platform="chatgpt")
        one = await provider.complete("what are the best crm tools?")
        two = await provider.complete("what are the best crm tools?")
        assert one.text == two.text
        assert one.duration_ms > 0

    asyncio.run(run())


def test_mock_gsc_returns_rows() -> None:
    async def run():
        provider = MockGSCProvider()
        rows = await provider.fetch_queries("https://example.com", days_back=30, row_limit=50)
        assert len(rows) > 0
        assert all(r.impressions > 0 for r in rows)

    asyncio.run(run())


def test_mock_authority_stable_per_domain() -> None:
    async def run():
        provider = MockAuthorityProvider()
        a = await provider.authority_for("example.com")
        b = await provider.authority_for("example.com")
        assert a == b

    asyncio.run(run())


def test_mock_wikipedia() -> None:
    async def run():
        provider = MockWikipediaProvider()
        has, url = await provider.has_citation("wikipedia.org")
        assert isinstance(has, bool)
        if has:
            assert url and url.startswith("https://en.wikipedia.org/")

    asyncio.run(run())
