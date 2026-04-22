"""Provider registry.

Each external integration (LLMs, GSC, Ahrefs, Moz, Wikipedia, WebGraph) exposes
a Protocol in `base.py` and has both a `mock.*` and `real.*` implementation.
The factory functions here return the right one based on settings.
"""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.providers.base import (
    AuthorityProvider,
    GSCProvider,
    LLMProvider,
    WikipediaProvider,
)


def _should_use_real(key: str | None) -> bool:
    mode = (settings.PROVIDER_MODE or "auto").lower()
    if mode == "mock":
        return False
    if mode == "real":
        return True
    return bool(key)


@lru_cache(maxsize=1)
def get_openai_provider() -> LLMProvider:
    if _should_use_real(settings.OPENAI_API_KEY):
        from app.providers.real.openai_llm import OpenAILLMProvider
        return OpenAILLMProvider(settings.OPENAI_API_KEY or "")
    from app.providers.mock.llm import MockLLMProvider
    return MockLLMProvider(platform="chatgpt")


@lru_cache(maxsize=1)
def get_anthropic_provider() -> LLMProvider:
    if _should_use_real(settings.ANTHROPIC_API_KEY):
        from app.providers.real.anthropic_llm import AnthropicLLMProvider
        return AnthropicLLMProvider(settings.ANTHROPIC_API_KEY or "")
    from app.providers.mock.llm import MockLLMProvider
    return MockLLMProvider(platform="claude")


@lru_cache(maxsize=1)
def get_perplexity_provider() -> LLMProvider:
    if _should_use_real(settings.PERPLEXITY_API_KEY):
        from app.providers.real.perplexity_llm import PerplexityLLMProvider
        return PerplexityLLMProvider(settings.PERPLEXITY_API_KEY or "")
    from app.providers.mock.llm import MockLLMProvider
    return MockLLMProvider(platform="perplexity")


@lru_cache(maxsize=1)
def get_google_ai_provider() -> LLMProvider:
    if _should_use_real(settings.GOOGLE_AI_API_KEY):
        from app.providers.real.google_ai_llm import GoogleAILLMProvider
        return GoogleAILLMProvider(settings.GOOGLE_AI_API_KEY or "")
    from app.providers.mock.llm import MockLLMProvider
    return MockLLMProvider(platform="google_ai")


def get_llm_provider(platform: str) -> LLMProvider:
    """Return a provider keyed by platform slug."""
    mapping = {
        "chatgpt": get_openai_provider,
        "claude": get_anthropic_provider,
        "perplexity": get_perplexity_provider,
        "google_ai": get_google_ai_provider,
        "gemini": get_google_ai_provider,
    }
    fn = mapping.get(platform)
    if not fn:
        from app.providers.mock.llm import MockLLMProvider
        return MockLLMProvider(platform=platform)
    return fn()


@lru_cache(maxsize=1)
def get_gsc_provider() -> GSCProvider:
    if _should_use_real(settings.GSC_CREDENTIALS_PATH):
        from app.providers.real.gsc import RealGSCProvider
        return RealGSCProvider(settings.GSC_CREDENTIALS_PATH)
    from app.providers.mock.gsc import MockGSCProvider
    return MockGSCProvider()


@lru_cache(maxsize=1)
def get_authority_provider() -> AuthorityProvider:
    has_any = settings.AHREFS_API_KEY or settings.MOZ_API_KEY
    if _should_use_real(has_any):
        from app.providers.real.authority import CompositeAuthorityProvider
        return CompositeAuthorityProvider()
    from app.providers.mock.authority import MockAuthorityProvider
    return MockAuthorityProvider()


@lru_cache(maxsize=1)
def get_wikipedia_provider() -> WikipediaProvider:
    # Wikipedia has a public API — always "real" unless mode forced to mock.
    if (settings.PROVIDER_MODE or "auto").lower() == "mock":
        from app.providers.mock.authority import MockWikipediaProvider
        return MockWikipediaProvider()
    from app.providers.real.wikipedia import RealWikipediaProvider
    return RealWikipediaProvider()
