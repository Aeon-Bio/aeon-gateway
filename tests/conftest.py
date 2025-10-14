"""
Pytest fixtures for tests

Shared fixtures available to all tests:
- sarah_profile: UserContext for demo user
- sf_to_la_query: QueryRequest for demo scenario
- mock_agentic_system: MockAgenticSystem instance
"""
import pytest
from src.models.gateway import get_sarah_profile, get_sf_to_la_query
from tests.mocks.agentic_system import MockAgenticSystem


@pytest.fixture
def sarah_profile():
    """Sarah's user profile for testing"""
    return get_sarah_profile()


@pytest.fixture
def sf_to_la_query():
    """Sarah's SF→LA query for testing"""
    return get_sf_to_la_query()


@pytest.fixture
def mock_agentic_system():
    """Mock agentic system instance"""
    return MockAgenticSystem()
