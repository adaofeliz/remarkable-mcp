import pytest

from remarkable_mcp.cache import document_cache


@pytest.fixture(autouse=True)
def reset_document_cache():
    """Reset the shared document cache before each test to prevent cross-test contamination."""
    document_cache.invalidate()
    yield
    document_cache.invalidate()
