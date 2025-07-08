"""Jira formatting utilities for markdown generation."""

import re
from datetime import datetime
from typing import Dict, List, Optional


def format_date(date_str: Optional[str]) -> str:
    """Format date string for better readability.

    Args:
        date_str: ISO date string or None

    Returns:
        Formatted date string
    """
    if not date_str:
        return "Not set"
    try:
        # Parse the datetime string and format it nicely
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str


def get_issue_status_emoji(status_name: str) -> str:
    """Get emoji for issue status.

    Args:
        status_name: Status name from Jira

    Returns:
        Emoji string for the status
    """
    status_map = {
        "To Do": "📋",
        "Backlog": "📝",
        "In Progress": "🔄",
        "In Review": "👀",
        "Done": "✅",
        "Closed": "🔒",
        "Open": "🔓",
    }
    return status_map.get(status_name, "📌")


def get_issue_type_emoji(issue_type: str) -> str:
    """Get emoji for issue type.

    Args:
        issue_type: Issue type name from Jira

    Returns:
        Emoji string for the issue type
    """
    type_map = {
        "Task": "📋",
        "Story": "📖",
        "Bug": "🐛",
        "Epic": "🎯",
        "Sub-task": "📄",
    }
    return type_map.get(issue_type, "📄")


def get_priority_emoji(priority: Optional[str]) -> str:
    """Get emoji for priority.

    Args:
        priority: Priority name from Jira or None

    Returns:
        Emoji string for the priority
    """
    if not priority:
        return "⚪"
    priority_map = {
        "Highest": "🔴",
        "High": "🟠",
        "Normal": "🟡",
        "Low": "🟢",
        "Lowest": "🔵",
    }
    return priority_map.get(priority, "⚪")


def add_ticket_links(
    text: str, jira_base_url: str = "https://mercari.atlassian.net"
) -> str:
    """Add ticket links for any JIRA ticket references in text.

    Args:
        text: Text that may contain ticket references
        jira_base_url: Base URL for Jira instance

    Returns:
        Text with ticket references converted to markdown links
    """
    ticket_pattern = r"\b([A-Z][A-Z0-9]*-\d+)\b"
    return re.sub(
        ticket_pattern,
        rf"[\1]({jira_base_url}/browse/\1)",
        text,
    )


def format_issue_details_table(
    fields: Dict,
    include_story_points: bool = True,
    include_labels: bool = True,
) -> List[str]:
    """Format issue details as a markdown table.

    Args:
        fields: Issue fields dictionary
        include_story_points: Whether to include story points if available
        include_labels: Whether to include labels if available

    Returns:
        List of markdown table rows
    """
    status_emoji = get_issue_status_emoji(fields["status"]["name"])
    priority_emoji = get_priority_emoji(fields.get("priority", {}).get("name"))

    rows = [
        "| Field | Value |",
        "|-------|-------|",
        f"| **Priority** | {priority_emoji} {fields.get('priority', {}).get('name', 'None')} |",
        f"| **Status** | {status_emoji} {fields['status']['name']} |",
        f"| **Assignee** | {fields.get('assignee', {}).get('display_name', 'Unassigned') if fields.get('assignee') else 'Unassigned'} |",
        f"| **Reporter** | {fields.get('reporter', {}).get('display_name', 'Unknown') if fields.get('reporter') else 'Unknown'} |",
        f"| **Created** | {format_date(fields.get('created'))} |",
        f"| **Updated** | {format_date(fields.get('updated'))} |",
    ]

    if include_story_points and fields.get("story_points"):
        rows.append(f"| **Story Points** | {fields['story_points']} |")

    if include_labels and fields.get("labels"):
        labels_str = ", ".join([f"`{label}`" for label in fields["labels"]])
        rows.append(f"| **Labels** | {labels_str} |")

    return rows


def format_description_blockquote(
    description_text: str,
    jira_base_url: str = "https://mercari.atlassian.net",
) -> List[str]:
    """Format description as blockquote with ticket links.

    Args:
        description_text: Description text
        jira_base_url: Base URL for Jira instance

    Returns:
        List of markdown blockquote lines
    """
    if not description_text or not description_text.strip():
        return ["> No description provided"]

    lines = []
    description_lines = description_text.strip().split("\n")

    for line in description_lines:
        if line.strip():
            linked_line = add_ticket_links(line.strip(), jira_base_url)
            lines.append(f"> {linked_line}")
        else:
            lines.append(">")

    return lines
