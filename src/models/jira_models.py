"""Pydantic models for Jira data structures."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JiraUser(BaseModel):
    """Jira user model."""

    account_id: str = Field(..., alias="accountId")
    display_name: str = Field(..., alias="displayName")
    email_address: Optional[str] = Field(None, alias="emailAddress")
    active: bool = True

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class JiraStatus(BaseModel):
    """Jira status model."""

    id: str
    name: str
    status_category: Dict[str, Any] = Field(..., alias="statusCategory")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class JiraIssueType(BaseModel):
    """Jira issue type model."""

    id: str
    name: str
    description: Optional[str] = None
    icon_url: str = Field(..., alias="iconUrl")
    subtask: bool = False

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class JiraPriority(BaseModel):
    """Jira priority model."""

    id: str
    name: str
    icon_url: str = Field(..., alias="iconUrl")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class JiraProject(BaseModel):
    """Jira project model."""

    id: str
    key: str
    name: str
    project_type_key: str = Field(..., alias="projectTypeKey")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class JiraIssueFields(BaseModel):
    """Jira issue fields model."""

    summary: str
    description: Optional[Any] = (
        None  # Can be string or ADF (Atlassian Document Format)
    )
    status: JiraStatus
    issue_type: JiraIssueType = Field(..., alias="issuetype")
    priority: Optional[JiraPriority] = None
    assignee: Optional[JiraUser] = None
    reporter: Optional[JiraUser] = None
    creator: Optional[JiraUser] = None
    project: JiraProject
    created: datetime
    updated: datetime
    resolved: Optional[datetime] = None
    labels: List[str] = []
    components: List[Dict[str, Any]] = []
    fix_versions: List[Dict[str, Any]] = Field([], alias="fixVersions")
    affects_versions: List[Dict[str, Any]] = Field([], alias="versions")
    story_points: Optional[float] = Field(None, alias="customfield_10016")
    epic_link: Optional[str] = Field(None, alias="customfield_10014")
    sprint: Optional[List[Dict[str, Any]]] = Field(None, alias="customfield_10020")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class JiraIssue(BaseModel):
    """Jira issue model."""

    id: str
    key: str
    self: str
    fields: JiraIssueFields

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class JiraSearchResult(BaseModel):
    """Jira search result model."""

    expand: Optional[str] = None
    start_at: int = Field(..., alias="startAt")
    max_results: int = Field(..., alias="maxResults")
    total: int
    issues: List[JiraIssue]

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class EpicDownloadResult(BaseModel):
    """Result of epic download operation."""

    epic_key: str
    epic_summary: str
    total_issues: int
    total_subtasks: int
    issues: List[JiraIssue]
    subtasks: Dict[str, List[JiraIssue]]  # Maps story key to its sub-tasks
    download_timestamp: datetime
    output_file: str


class StoryDownloadResult(BaseModel):
    """Result of story download operation."""

    story_key: str
    story_summary: str
    total_subtasks: int
    story_issue: JiraIssue
    subtasks: List[JiraIssue]
    download_timestamp: datetime
    output_file: str
