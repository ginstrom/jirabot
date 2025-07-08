"""Jira API client for interacting with Jira REST API."""

import asyncio
import logging
from typing import Dict, List, Optional

import aiohttp
from asyncio_throttle import Throttler

from ..config.settings import settings
from ..models.jira_models import JiraIssue, JiraSearchResult

logger = logging.getLogger(__name__)


class JiraClient:
    """Async Jira API client with rate limiting and error handling."""

    def __init__(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        api_token: Optional[str] = None,
        rate_limit: int = 10,
    ):
        """Initialize Jira client.

        Args:
            url: Jira instance URL
            username: Jira username
            api_token: Jira API token
            rate_limit: Requests per second limit
        """
        self.url = url or settings().jira_url
        self.username = username or settings().jira_username
        self.api_token = api_token or settings().jira_api_token
        self.base_url = f"{self.url.rstrip('/')}/rest/api/3"

        # Rate limiting
        self.throttler = Throttler(rate_limit=rate_limit)

        # Session will be created when needed
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with authentication."""
        if self._session is None or self._session.closed:
            auth = aiohttp.BasicAuth(self.username, self.api_token)
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                auth=auth,
                timeout=timeout,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict:
        """Make rate-limited HTTP request to Jira API.

        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data

        Returns:
            JSON response data

        Raises:
            aiohttp.ClientError: For HTTP errors
        """
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        async with self.throttler:
            logger.debug(f"Making {method} request to {url}")

            async with session.request(
                method, url, params=params, json=data
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def get_issue(self, issue_key: str) -> JiraIssue:
        """Get a single issue by key.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')

        Returns:
            JiraIssue object
        """
        data = await self._make_request("GET", f"issue/{issue_key}")
        return JiraIssue(**data)

    async def search_issues(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
        start_at: int = 0,
        max_results: int = 100,
    ) -> JiraSearchResult:
        """Search for issues using JQL.

        Args:
            jql: JQL query string
            fields: List of fields to return
            expand: List of fields to expand
            start_at: Starting index for pagination
            max_results: Maximum results to return

        Returns:
            JiraSearchResult object
        """
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
        }

        if fields:
            params["fields"] = ",".join(fields)

        if expand:
            params["expand"] = ",".join(expand)

        data = await self._make_request("GET", "search", params=params)
        return JiraSearchResult(**data)

    async def get_epic_issues(
        self, epic_key: str, fields: Optional[List[str]] = None
    ) -> List[JiraIssue]:
        """Get all issues in an epic.

        Args:
            epic_key: Epic key (e.g., 'PROJ-123')
            fields: List of fields to return

        Returns:
            List of JiraIssue objects
        """
        jql = f'"Epic Link" = {epic_key}'
        issues = []
        start_at = 0
        max_results = 100

        logger.info(f"Fetching issues for epic {epic_key}")

        while True:
            result = await self.search_issues(
                jql=jql,
                fields=fields,
                start_at=start_at,
                max_results=max_results,
            )

            issues.extend(result.issues)

            if len(result.issues) < max_results:
                break

            start_at += max_results
            logger.info(f"Fetched {len(issues)} issues so far...")

        logger.info(f"Total issues found: {len(issues)}")
        return issues

    async def get_epic_info(self, epic_key: str) -> JiraIssue:
        """Get epic information.

        Args:
            epic_key: Epic key (e.g., 'PROJ-123')

        Returns:
            JiraIssue object for the epic
        """
        return await self.get_issue(epic_key)

    async def get_story_subtasks(
        self, story_key: str, fields: Optional[List[str]] = None
    ) -> List[JiraIssue]:
        """Get all sub-tasks of a story.

        Args:
            story_key: Story key (e.g., 'PROJ-123')
            fields: List of fields to return

        Returns:
            List of JiraIssue objects for sub-tasks
        """
        jql = f"parent = {story_key}"
        issues = []
        start_at = 0
        max_results = 100

        logger.info(f"Fetching sub-tasks for story {story_key}")

        while True:
            result = await self.search_issues(
                jql=jql,
                fields=fields,
                start_at=start_at,
                max_results=max_results,
            )

            issues.extend(result.issues)

            if len(result.issues) < max_results:
                break

            start_at += max_results
            logger.info(f"Fetched {len(issues)} sub-tasks so far...")

        logger.info(f"Total sub-tasks found: {len(issues)}")
        return issues

    async def get_story_info(self, story_key: str) -> JiraIssue:
        """Get story information.

        Args:
            story_key: Story key (e.g., 'PROJ-123')

        Returns:
            JiraIssue object for the story
        """
        return await self.get_issue(story_key)
