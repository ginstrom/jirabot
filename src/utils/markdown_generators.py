"""Markdown generation utilities for Jira exports."""

from collections import defaultdict
from typing import Dict, List, Optional

from .jira_formatters import (
    format_date,
    get_issue_status_emoji,
    get_issue_type_emoji,
    get_priority_emoji,
    format_issue_details_table,
    format_description_blockquote,
)


def generate_summary_statistics(
    issues: List[Dict],
    subtasks: Optional[Dict[str, List[Dict]]] = None,
) -> Dict[str, Dict]:
    """Generate summary statistics for issues and subtasks.

    Args:
        issues: List of issue dictionaries
        subtasks: Optional dictionary mapping story keys to their subtasks

    Returns:
        Dictionary containing statistics for issue types, statuses, priorities, and assignees
    """
    issue_types = defaultdict(int)
    statuses = defaultdict(int)
    priorities = defaultdict(int)
    assignees = defaultdict(int)

    # Analyze main issues
    for issue in issues:
        fields = issue["fields"]
        issue_types[fields["issue_type"]["name"]] += 1
        statuses[fields["status"]["name"]] += 1

        if fields.get("priority"):
            priorities[fields["priority"]["name"]] += 1
        else:
            priorities["None"] += 1

        if fields.get("assignee"):
            assignees[fields["assignee"]["display_name"]] += 1
        else:
            assignees["Unassigned"] += 1

    # Analyze sub-tasks if provided
    if subtasks:
        for story_key, story_subtasks in subtasks.items():
            for subtask in story_subtasks:
                fields = subtask["fields"]
                issue_types[fields["issue_type"]["name"]] += 1
                statuses[fields["status"]["name"]] += 1

                if fields.get("priority"):
                    priorities[fields["priority"]["name"]] += 1
                else:
                    priorities["None"] += 1

                if fields.get("assignee"):
                    assignees[fields["assignee"]["display_name"]] += 1
                else:
                    assignees["Unassigned"] += 1

    return {
        "issue_types": dict(issue_types),
        "statuses": dict(statuses),
        "priorities": dict(priorities),
        "assignees": dict(assignees),
    }


def generate_statistics_markdown(stats: Dict[str, Dict]) -> List[str]:
    """Generate markdown for summary statistics.

    Args:
        stats: Statistics dictionary from generate_summary_statistics

    Returns:
        List of markdown lines
    """
    md_lines = []

    # Issue Types
    md_lines.append("### Issue Types")
    for issue_type, count in sorted(stats["issue_types"].items()):
        emoji = get_issue_type_emoji(issue_type)
        md_lines.append(f"- {emoji} **{issue_type}**: {count}")
    md_lines.append("")

    # Status Distribution
    md_lines.append("### Status Distribution")
    for status, count in sorted(stats["statuses"].items()):
        emoji = get_issue_status_emoji(status)
        md_lines.append(f"- {emoji} **{status}**: {count}")
    md_lines.append("")

    # Priority Distribution
    md_lines.append("### Priority Distribution")
    for priority, count in sorted(stats["priorities"].items()):
        emoji = get_priority_emoji(priority)
        md_lines.append(f"- {emoji} **{priority}**: {count}")
    md_lines.append("")

    # Top Assignees
    md_lines.append("### Top Assignees")
    sorted_assignees = sorted(
        stats["assignees"].items(), key=lambda x: x[1], reverse=True
    )[:10]
    for assignee, count in sorted_assignees:
        md_lines.append(
            f"- **{assignee}**: {count} {'issue' if count == 1 else 'issues'}"
        )
    md_lines.append("")

    return md_lines


def generate_table_of_contents(
    issue_types: List[str],
    include_summary: bool = True,
    include_main_section: bool = True,
    main_section_title: str = "All Issues",
) -> List[str]:
    """Generate table of contents for markdown.

    Args:
        issue_types: List of issue type names
        include_summary: Whether to include summary statistics section
        include_main_section: Whether to include main issues section
        main_section_title: Title for main section

    Returns:
        List of markdown lines
    """
    md_lines = []
    md_lines.append("## 📋 Table of Contents")
    md_lines.append("")

    if include_summary:
        md_lines.append("- [Summary Statistics](#📊-summary-statistics)")

    if include_main_section:
        anchor = main_section_title.lower().replace(" ", "-")
        md_lines.append(f"- [{main_section_title}](#🎫-{anchor})")

    # Group issues by type for TOC
    for issue_type in sorted(issue_types):
        anchor = issue_type.lower().replace(" ", "-").replace("/", "")
        md_lines.append(f"  - [{issue_type}](#🔸-{anchor})")
    md_lines.append("")

    return md_lines


def generate_issue_section(
    issue: Dict,
    jira_base_url: str = "https://mercari.atlassian.net",
    include_subtasks: bool = False,
    subtasks: Optional[List[Dict]] = None,
) -> List[str]:
    """Generate markdown section for a single issue.

    Args:
        issue: Issue dictionary
        jira_base_url: Base URL for Jira instance
        include_subtasks: Whether to include subtasks section
        subtasks: List of subtask dictionaries

    Returns:
        List of markdown lines
    """
    md_lines = []
    fields = issue["fields"]

    # Issue header with link
    status_emoji = get_issue_status_emoji(fields["status"]["name"])
    priority_emoji = get_priority_emoji(fields.get("priority", {}).get("name"))

    md_lines.append(
        f"#### {status_emoji} [{issue['key']}]({jira_base_url}/browse/{issue['key']}) - {fields['summary']}"
    )
    md_lines.append("")

    # Issue details table
    md_lines.extend(format_issue_details_table(fields))
    md_lines.append("")

    # Description with ticket linking
    if fields.get("description_text"):
        md_lines.append("**Description:**")
        md_lines.append("")
        md_lines.extend(
            format_description_blockquote(fields["description_text"], jira_base_url)
        )
        md_lines.append("")

    # Add sub-tasks if requested and available
    if include_subtasks and subtasks:
        md_lines.append("##### 📋 Sub-tasks")
        md_lines.append("")

        for subtask in subtasks:
            subtask_fields = subtask["fields"]
            subtask_status_emoji = get_issue_status_emoji(
                subtask_fields["status"]["name"]
            )
            subtask_priority_emoji = get_priority_emoji(
                subtask_fields.get("priority", {}).get("name")
            )

            md_lines.append(
                f"- {subtask_status_emoji} **[{subtask['key']}]({jira_base_url}/browse/{subtask['key']})** - {subtask_fields['summary']}"
            )
            md_lines.append(
                f"  - **Priority:** {subtask_priority_emoji} {subtask_fields.get('priority', {}).get('name', 'None')}"
            )
            md_lines.append(
                f"  - **Status:** {subtask_status_emoji} {subtask_fields['status']['name']}"
            )
            md_lines.append(
                f"  - **Assignee:** {subtask_fields.get('assignee', {}).get('display_name', 'Unassigned') if subtask_fields.get('assignee') else 'Unassigned'}"
            )

            if subtask_fields.get("description_text"):
                description = subtask_fields["description_text"].strip()
                if description:
                    # Show first line of description
                    first_line = description.split("\n")[0]
                    if len(first_line) > 80:
                        first_line = first_line[:80] + "..."
                    md_lines.append(f"  - **Description:** {first_line}")

            md_lines.append("")

        md_lines.append("")

    md_lines.append("---")
    md_lines.append("")

    return md_lines


def generate_export_footer(
    item_type: str,
    item_key: str,
    item_summary: str,
    total_items: int,
    total_subtasks: int,
    download_timestamp: str,
    jira_base_url: str = "https://mercari.atlassian.net",
) -> List[str]:
    """Generate export information footer.

    Args:
        item_type: Type of item (Epic, Story, etc.)
        item_key: Item key (e.g., PROJ-123)
        item_summary: Item summary
        total_items: Total number of items exported
        total_subtasks: Total number of subtasks exported
        download_timestamp: Download timestamp
        jira_base_url: Base URL for Jira instance

    Returns:
        List of markdown lines
    """
    md_lines = []
    md_lines.append("## ℹ️ Export Information")
    md_lines.append("")
    md_lines.append(
        f"- **Source {item_type}:** [{item_key}]({jira_base_url}/browse/{item_key})"
    )
    md_lines.append(f"- **Export Date:** {format_date(download_timestamp)}")

    if item_type.lower() == "epic":
        md_lines.append(f"- **Total Issues Exported:** {total_items}")
        md_lines.append(f"- **Total Sub-tasks Exported:** {total_subtasks}")
        md_lines.append(f"- **Generated by:** Jirabot Epic Exporter")
    elif item_type.lower() == "story":
        md_lines.append(f"- **Total Sub-tasks Exported:** {total_subtasks}")
        md_lines.append(f"- **Generated by:** Jirabot Story Exporter")

    return md_lines
