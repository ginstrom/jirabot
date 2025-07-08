#!/usr/bin/env python3
"""Unit tests for scripts.download_story_subtasks.py"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, mock_open
from datetime import datetime
from pathlib import Path
import json

from src.models.jira_models import StoryDownloadResult, JiraIssue, JiraIssueFields
from scripts.download_story_subtasks import (
    create_markdown_from_story_data,
    download_story_subtasks,
    main,
)


class TestCreateMarkdownFromStoryData:
    """Test cases for create_markdown_from_story_data function."""

    @pytest.fixture
    def sample_story_data(self):
        """Sample story data for testing."""
        return {
            "story_key": "PROJ-123",
            "story_summary": "Test Story Summary",
            "total_subtasks": 2,
            "download_timestamp": "2024-01-15T10:30:00",
            "story_issue": {
                "fields": {
                    "summary": "Test Story Summary",
                    "description_text": "This is a test story description",
                    "status": {"name": "In Progress"},
                    "priority": {"name": "High"},
                    "assignee": {"display_name": "John Doe"},
                    "reporter": {"display_name": "Jane Smith"},
                    "created": "2024-01-01T09:00:00.000+0000",
                    "updated": "2024-01-15T10:00:00.000+0000",
                    "issue_type": {"name": "Story"},
                }
            },
            "subtasks": [
                {
                    "key": "PROJ-124",
                    "fields": {
                        "summary": "Subtask 1",
                        "description_text": "First subtask description",
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "assignee": {"display_name": "Alice Johnson"},
                        "reporter": {"display_name": "Bob Wilson"},
                        "created": "2024-01-02T09:00:00.000+0000",
                        "updated": "2024-01-15T09:30:00.000+0000",
                        "issue_type": {"name": "Sub-task"},
                    },
                },
                {
                    "key": "PROJ-125",
                    "fields": {
                        "summary": "Subtask 2",
                        "description_text": "Second subtask description",
                        "status": {"name": "Done"},
                        "priority": {"name": "Low"},
                        "assignee": {"display_name": "Charlie Brown"},
                        "reporter": {"display_name": "Diana Prince"},
                        "created": "2024-01-03T09:00:00.000+0000",
                        "updated": "2024-01-15T11:00:00.000+0000",
                        "issue_type": {"name": "Sub-task"},
                    },
                },
            ],
        }

    def test_create_markdown_with_subtasks(self, sample_story_data):
        """Test markdown generation with subtasks."""
        result = create_markdown_from_story_data(sample_story_data)

        # Check title
        assert (
            "# Story: [PROJ-123](https://mercari.atlassian.net/browse/PROJ-123) - Test Story Summary"
            in result
        )

        # Check basic information
        assert "**Total Sub-tasks:** 2" in result
        assert "**Download Date:**" in result

        # Check story information section
        assert "## 📖 Story Information" in result

        # Check story description
        assert "### 📝 Story Description" in result
        assert "This is a test story description" in result

        # Check summary statistics
        assert "## 📊 Sub-tasks Summary Statistics" in result

        # Check table of contents
        assert "## 📋 Table of Contents" in result

        # Check sub-tasks section
        assert "## 📋 All Sub-tasks" in result
        assert "### 🔸 Sub-task" in result

        # Check subtask details
        assert "PROJ-124" in result
        assert "Subtask 1" in result
        assert "PROJ-125" in result
        assert "Subtask 2" in result

    def test_create_markdown_no_subtasks(self, sample_story_data):
        """Test markdown generation without subtasks."""
        sample_story_data["subtasks"] = []
        sample_story_data["total_subtasks"] = 0

        result = create_markdown_from_story_data(sample_story_data)

        # Check title
        assert (
            "# Story: [PROJ-123](https://mercari.atlassian.net/browse/PROJ-123) - Test Story Summary"
            in result
        )

        # Check no subtasks message
        assert "No sub-tasks found for this story." in result

        # Should not have summary statistics or table of contents
        assert "## 📊 Sub-tasks Summary Statistics" not in result
        assert "## 📋 Table of Contents" not in result

    def test_create_markdown_custom_jira_url(self, sample_story_data):
        """Test markdown generation with custom Jira URL."""
        custom_url = "https://mycompany.atlassian.net"
        result = create_markdown_from_story_data(sample_story_data, custom_url)

        assert f"[PROJ-123]({custom_url}/browse/PROJ-123)" in result

    def test_create_markdown_no_description(self, sample_story_data):
        """Test markdown generation when story has no description."""
        sample_story_data["story_issue"]["fields"]["description_text"] = None

        result = create_markdown_from_story_data(sample_story_data)

        # Should not have description section
        assert "### 📝 Story Description" not in result


class TestDownloadStorySubtasks:
    """Test cases for download_story_subtasks function."""

    @pytest.fixture
    def mock_jira_issue(self):
        """Mock Jira issue object."""
        return JiraIssue(
            id="123456",
            key="PROJ-123",
            self="https://mercari.atlassian.net/rest/api/2/issue/123456",
            fields=JiraIssueFields(
                summary="Test Story Summary",
                description={
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": "Test description"}],
                        }
                    ],
                },
                status={
                    "id": "1",
                    "name": "In Progress",
                    "statusCategory": {"key": "indeterminate", "name": "In Progress"},
                },
                priority={
                    "id": "2",
                    "name": "High",
                    "iconUrl": "https://mercari.atlassian.net/images/icons/priorities/high.svg",
                },
                assignee={
                    "accountId": "user123",
                    "displayName": "John Doe",
                    "emailAddress": "john.doe@example.com",
                },
                reporter={
                    "accountId": "user456",
                    "displayName": "Jane Smith",
                    "emailAddress": "jane.smith@example.com",
                },
                project={
                    "id": "10001",
                    "key": "PROJ",
                    "name": "Test Project",
                    "projectTypeKey": "software",
                },
                created="2024-01-01T09:00:00.000+0000",
                updated="2024-01-15T10:00:00.000+0000",
                issue_type={
                    "id": "10001",
                    "name": "Story",
                    "iconUrl": "https://mercari.atlassian.net/images/icons/issuetypes/story.svg",
                },
            ),
        )

    @pytest.fixture
    def mock_subtasks(self):
        """Mock subtasks list."""
        return [
            JiraIssue(
                id="123457",
                key="PROJ-124",
                self="https://mercari.atlassian.net/rest/api/2/issue/123457",
                fields=JiraIssueFields(
                    summary="Subtask 1",
                    description={
                        "type": "doc",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {"type": "text", "text": "Subtask 1 description"}
                                ],
                            }
                        ],
                    },
                    status={
                        "id": "10001",
                        "name": "To Do",
                        "statusCategory": {"key": "new", "name": "To Do"},
                    },
                    priority={
                        "id": "3",
                        "name": "Medium",
                        "iconUrl": "https://mercari.atlassian.net/images/icons/priorities/medium.svg",
                    },
                    assignee={
                        "accountId": "user789",
                        "displayName": "Alice Johnson",
                        "emailAddress": "alice.johnson@example.com",
                    },
                    reporter={
                        "accountId": "user456",
                        "displayName": "Bob Wilson",
                        "emailAddress": "bob.wilson@example.com",
                    },
                    project={
                        "id": "10001",
                        "key": "PROJ",
                        "name": "Test Project",
                        "projectTypeKey": "software",
                    },
                    created="2024-01-02T09:00:00.000+0000",
                    updated="2024-01-15T09:30:00.000+0000",
                    issue_type={
                        "id": "10003",
                        "name": "Sub-task",
                        "iconUrl": "https://mercari.atlassian.net/images/icons/issuetypes/subtask.svg",
                        "subtask": True,
                    },
                ),
            )
        ]

    @pytest.mark.asyncio
    async def test_download_story_subtasks_success(
        self, mock_jira_issue, mock_subtasks, tmp_path
    ):
        """Test successful download of story and subtasks."""
        with patch("scripts.download_story_subtasks.JiraClient") as mock_jira_client, patch(
            "scripts.download_story_subtasks.ensure_directory_exists"
        ) as mock_ensure_dir, patch(
            "scripts.download_story_subtasks.get_file_size"
        ) as mock_get_size, patch(
            "scripts.download_story_subtasks.extract_text_from_adf"
        ) as mock_extract_text, patch(
            "builtins.open", mock_open()
        ) as mock_file:

            # Setup mocks
            mock_jira_instance = AsyncMock()
            mock_jira_client.return_value.__aenter__.return_value = mock_jira_instance
            mock_jira_instance.get_story_info.return_value = mock_jira_issue
            mock_jira_instance.get_story_subtasks.return_value = mock_subtasks
            mock_get_size.return_value = 1024
            mock_extract_text.return_value = "Extracted text"

            # Test the function
            result = await download_story_subtasks(
                story_key="PROJ-123",
                output_dir=str(tmp_path),
                output_filename="test_story.md",
            )

            # Verify result
            assert isinstance(result, StoryDownloadResult)
            assert result.story_key == "PROJ-123"
            assert result.story_summary == "Test Story Summary"
            assert result.total_subtasks == 1
            assert result.story_issue == mock_jira_issue
            assert result.subtasks == mock_subtasks
            assert result.output_file == str(tmp_path / "test_story.md")

            # Verify mocks were called
            mock_ensure_dir.assert_called_once_with(str(tmp_path))
            mock_jira_instance.get_story_info.assert_called_once_with("PROJ-123")
            mock_jira_instance.get_story_subtasks.assert_called_once_with("PROJ-123")
            mock_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_story_subtasks_default_params(
        self, mock_jira_issue, mock_subtasks
    ):
        """Test download with default parameters."""
        with patch("scripts.download_story_subtasks.JiraClient") as mock_jira_client, patch(
            "scripts.download_story_subtasks.ensure_directory_exists"
        ) as mock_ensure_dir, patch(
            "scripts.download_story_subtasks.get_file_size"
        ) as mock_get_size, patch(
            "scripts.download_story_subtasks.extract_text_from_adf"
        ) as mock_extract_text, patch(
            "scripts.download_story_subtasks.settings"
        ) as mock_settings, patch(
            "scripts.download_story_subtasks.generate_timestamp_filename"
        ) as mock_timestamp, patch(
            "builtins.open", mock_open()
        ) as mock_file:

            # Setup mocks
            mock_jira_instance = AsyncMock()
            mock_jira_client.return_value.__aenter__.return_value = mock_jira_instance
            mock_jira_instance.get_story_info.return_value = mock_jira_issue
            mock_jira_instance.get_story_subtasks.return_value = mock_subtasks
            mock_get_size.return_value = 1024
            mock_extract_text.return_value = "Extracted text"
            mock_settings.return_value.output_dir = "./output"
            mock_timestamp.return_value = "story_PROJ-123_20240115_103000.json"

            # Test with default parameters
            result = await download_story_subtasks("PROJ-123")

            # Verify default settings were used
            mock_settings.assert_called_once()
            mock_ensure_dir.assert_called_once_with("./output")
            mock_timestamp.assert_called_once_with("story_PROJ-123")

    @pytest.mark.asyncio
    async def test_download_story_subtasks_jira_error(
        self, mock_jira_issue, mock_subtasks
    ):
        """Test error handling when Jira client fails."""
        with patch("scripts.download_story_subtasks.JiraClient") as mock_jira_client, patch(
            "scripts.download_story_subtasks.ensure_directory_exists"
        ):

            # Setup mock to raise exception
            mock_jira_instance = AsyncMock()
            mock_jira_client.return_value.__aenter__.return_value = mock_jira_instance
            mock_jira_instance.get_story_info.side_effect = Exception("Jira API Error")

            # Test that exception is raised
            with pytest.raises(Exception, match="Jira API Error"):
                await download_story_subtasks("PROJ-123")

    @pytest.mark.asyncio
    async def test_download_story_subtasks_no_subtasks(self, mock_jira_issue, tmp_path):
        """Test download when story has no subtasks."""
        with patch("scripts.download_story_subtasks.JiraClient") as mock_jira_client, patch(
            "scripts.download_story_subtasks.ensure_directory_exists"
        ) as mock_ensure_dir, patch(
            "scripts.download_story_subtasks.get_file_size"
        ) as mock_get_size, patch(
            "scripts.download_story_subtasks.extract_text_from_adf"
        ) as mock_extract_text, patch(
            "builtins.open", mock_open()
        ) as mock_file:

            # Setup mocks
            mock_jira_instance = AsyncMock()
            mock_jira_client.return_value.__aenter__.return_value = mock_jira_instance
            mock_jira_instance.get_story_info.return_value = mock_jira_issue
            mock_jira_instance.get_story_subtasks.return_value = []  # No subtasks
            mock_get_size.return_value = 512
            mock_extract_text.return_value = "Extracted text"

            # Test the function
            result = await download_story_subtasks(
                story_key="PROJ-123",
                output_dir=str(tmp_path),
                output_filename="test_story.md",
            )

            # Verify result
            assert result.total_subtasks == 0
            assert result.subtasks == []


class TestMainFunction:
    """Test cases for the main CLI function."""

    @patch("scripts.download_story_subtasks.asyncio.run")
    @patch("scripts.download_story_subtasks.print_success_message")
    @patch("scripts.download_story_subtasks.validate_settings")
    @patch("scripts.download_story_subtasks.setup_logging")
    def test_main_success(
        self,
        mock_setup_logging,
        mock_validate_settings,
        mock_print_success,
        mock_asyncio_run,
    ):
        """Test successful execution of main function."""
        # Setup mock result
        mock_result = Mock()
        mock_result.story_key = "PROJ-123"
        mock_result.story_summary = "Test Story"
        mock_result.total_subtasks = 2
        mock_result.output_file = "test_output.md"
        mock_asyncio_run.return_value = mock_result

        # Import and run main with Click runner
        from click.testing import CliRunner

        runner = CliRunner()

        result = runner.invoke(main, ["PROJ-123"])

        # Verify success
        assert result.exit_code == 0
        mock_setup_logging.assert_called_once_with(False)
        mock_validate_settings.assert_called_once_with(False)
        mock_print_success.assert_called_once()

    @patch("scripts.download_story_subtasks.asyncio.run")
    @patch("scripts.download_story_subtasks.handle_download_error")
    @patch("scripts.download_story_subtasks.validate_settings")
    @patch("scripts.download_story_subtasks.setup_logging")
    def test_main_error(
        self,
        mock_setup_logging,
        mock_validate_settings,
        mock_handle_error,
        mock_asyncio_run,
    ):
        """Test error handling in main function."""
        # Setup mock to raise exception
        mock_asyncio_run.side_effect = Exception("Download failed")

        # Import and run main with Click runner
        from click.testing import CliRunner

        runner = CliRunner()

        result = runner.invoke(main, ["PROJ-123"])

        # Verify error handling
        mock_handle_error.assert_called_once()
        assert "Download failed" in str(mock_handle_error.call_args[0][0])

    @patch("scripts.download_story_subtasks.asyncio.run")
    @patch("scripts.download_story_subtasks.print_success_message")
    @patch("scripts.download_story_subtasks.validate_settings")
    @patch("scripts.download_story_subtasks.setup_logging")
    def test_main_with_options(
        self,
        mock_setup_logging,
        mock_validate_settings,
        mock_print_success,
        mock_asyncio_run,
    ):
        """Test main function with all options."""
        # Setup mock result
        mock_result = Mock()
        mock_result.story_key = "PROJ-123"
        mock_result.story_summary = "Test Story"
        mock_result.total_subtasks = 2
        mock_result.output_file = "custom_output.md"
        mock_asyncio_run.return_value = mock_result

        # Import and run main with Click runner
        from click.testing import CliRunner

        runner = CliRunner()

        result = runner.invoke(
            main,
            [
                "PROJ-123",
                "--output-dir",
                "./custom_output",
                "--output-filename",
                "custom_story.md",
                "--verbose",
            ],
        )

        # Verify success with verbose logging
        assert result.exit_code == 0
        mock_setup_logging.assert_called_once_with(True)
        mock_validate_settings.assert_called_once_with(True)

        # Verify asyncio.run was called with correct parameters
        mock_asyncio_run.assert_called_once()
        call_args = mock_asyncio_run.call_args[0][0]
        # The call_args[0] should be a coroutine, but we can't easily inspect it
        # So we just verify the mock was called


class TestIntegration:
    """Integration tests for the entire download flow."""

    @pytest.mark.asyncio
    async def test_full_download_flow(self, tmp_path):
        """Test the complete download flow with mocked dependencies."""
        # Create mock objects instead of real Pydantic models
        mock_story = Mock()
        mock_story.key = "PROJ-123"
        mock_story.fields.summary = "Integration Test Story"
        mock_story.model_dump.return_value = {
            "key": "PROJ-123",
            "fields": {
                "summary": "Integration Test Story",
                "description": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "This is an integration test story.",
                                }
                            ],
                        }
                    ],
                },
                "status": {"name": "In Progress"},
                "priority": {"name": "High"},
                "assignee": {"display_name": "Test User"},
                "reporter": {"display_name": "Test Reporter"},
                "created": "2024-01-01T09:00:00.000+0000",
                "updated": "2024-01-15T10:00:00.000+0000",
                "issue_type": {"name": "Story"},
            },
        }

        mock_subtask = Mock()
        mock_subtask.model_dump.return_value = {
            "key": "PROJ-124",
            "fields": {
                "summary": "Test Subtask",
                "description": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "This is a test subtask."}
                            ],
                        }
                    ],
                },
                "status": {"name": "To Do"},
                "priority": {"name": "Medium"},
                "assignee": {"display_name": "Subtask User"},
                "reporter": {"display_name": "Subtask Reporter"},
                "created": "2024-01-02T09:00:00.000+0000",
                "updated": "2024-01-15T09:30:00.000+0000",
                "issue_type": {"name": "Sub-task"},
            },
        }
        mock_subtasks = [mock_subtask]

        with patch("scripts.download_story_subtasks.JiraClient") as mock_jira_client, patch(
            "scripts.download_story_subtasks.ensure_directory_exists"
        ) as mock_ensure_dir, patch(
            "scripts.download_story_subtasks.get_file_size"
        ) as mock_get_size, patch(
            "scripts.download_story_subtasks.extract_text_from_adf"
        ) as mock_extract_text, patch(
            "scripts.download_story_subtasks.StoryDownloadResult"
        ) as mock_result_class:

            # Setup mocks
            mock_jira_instance = AsyncMock()
            mock_jira_client.return_value.__aenter__.return_value = mock_jira_instance
            mock_jira_instance.get_story_info.return_value = mock_story
            mock_jira_instance.get_story_subtasks.return_value = mock_subtasks
            mock_get_size.return_value = 2048
            mock_extract_text.return_value = "Extracted text content"

            # Create output file path
            output_file = tmp_path / "integration_test.md"

            # Mock the result object
            mock_result = Mock()
            mock_result.story_key = "PROJ-123"
            mock_result.story_summary = "Integration Test Story"
            mock_result.total_subtasks = 1
            mock_result.output_file = str(output_file)
            mock_result_class.return_value = mock_result

            # Test the download function
            result = await download_story_subtasks(
                story_key="PROJ-123",
                output_dir=str(tmp_path),
                output_filename="integration_test.md",
            )

            # Verify the result
            assert result.story_key == "PROJ-123"
            assert result.story_summary == "Integration Test Story"
            assert result.total_subtasks == 1
            assert result.output_file == str(output_file)

            # Verify the markdown file was created with expected content
            assert output_file.exists()
            content = output_file.read_text(encoding="utf-8")
            assert "# Story: [PROJ-123]" in content
            assert "Integration Test Story" in content
            assert "Test Subtask" in content
            assert "📊 Sub-tasks Summary Statistics" in content
