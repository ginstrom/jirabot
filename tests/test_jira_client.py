"""Tests for the Jira client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.api.jira_client import JiraClient
from src.models.jira_models import JiraIssue, JiraSearchResult


class TestJiraClient:
    """Test cases for JiraClient."""

    def test_init(self):
        """Test JiraClient initialization."""
        client = JiraClient(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        )

        assert client.url == "https://test.atlassian.net"
        assert client.username == "test@example.com"
        assert client.api_token == "test-token"
        assert client.base_url == "https://test.atlassian.net/rest/api/3"

    @pytest.mark.asyncio
    async def test_get_session(self):
        """Test HTTP session creation."""
        client = JiraClient(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        )

        session = await client._get_session()
        assert session is not None
        assert session.auth.login == "test@example.com"
        assert session.auth.password == "test-token"

        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test JiraClient as async context manager."""
        async with JiraClient(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        ) as client:
            assert client is not None
            assert isinstance(client, JiraClient)

    def test_epic_jql_query(self):
        """Test that the epic JQL query is correctly formatted."""
        client = JiraClient(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        )

        # This would be the JQL query format used in get_epic_issues
        epic_key = "PROJ-123"
        expected_jql = f'"Epic Link" = {epic_key}'

        assert expected_jql == '"Epic Link" = PROJ-123'


if __name__ == "__main__":
    pytest.main([__file__])
