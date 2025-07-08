#!/usr/bin/env python3
"""Script to download all issues from a Jira epic and save them to Markdown."""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import defaultdict

import click
from dotenv import load_dotenv

# Add parent directory to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.jira_client import JiraClient
from src.config.settings import settings
from src.models.jira_models import EpicDownloadResult
from src.utils.file_utils import (
    ensure_directory_exists,
    extract_text_from_adf,
    format_file_size,
    generate_timestamp_filename,
    get_file_size,
)
from src.utils.jira_formatters import (
    format_date,
    get_issue_status_emoji,
    get_issue_type_emoji,
    get_priority_emoji,
)
from src.utils.markdown_generators import (
    generate_summary_statistics,
    generate_statistics_markdown,
    generate_table_of_contents,
    generate_issue_section,
    generate_export_footer,
)
from src.utils.cli_helpers import (
    setup_logging,
    validate_settings,
    print_success_message,
    handle_download_error,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def create_markdown_from_epic_data(
    epic_data, jira_base_url="https://mercari.atlassian.net"
):
    """Convert epic data to markdown format."""

    # Start building markdown content
    md_content = []

    # Title and Epic Information
    epic_key = epic_data["epic_key"]
    epic_summary = epic_data["epic_summary"]
    md_content.append(
        f"# Epic: [{epic_key}]({jira_base_url}/browse/{epic_key}) - {epic_summary}"
    )
    md_content.append("")
    md_content.append(
        f"**Download Date:** {format_date(epic_data.get('download_timestamp', ''))}"
    )
    md_content.append(f"**Total Issues:** {epic_data['total_issues']}")
    md_content.append(f"**Total Sub-tasks:** {epic_data.get('total_subtasks', 0)}")
    md_content.append("")

    # Generate summary statistics
    issues = epic_data["issues"]
    subtasks = epic_data.get("subtasks", {})

    stats = generate_summary_statistics(issues, subtasks)

    # Summary Statistics
    md_content.append("## 📊 Summary Statistics")
    md_content.append("")
    md_content.extend(generate_statistics_markdown(stats))

    # Table of Contents
    md_content.extend(generate_table_of_contents(list(stats["issue_types"].keys())))

    # All Issues Section
    md_content.append("## 🎫 All Issues")
    md_content.append("")

    # Group issues by type
    issues_by_type = defaultdict(list)
    for issue in issues:
        issue_type = issue["fields"]["issue_type"]["name"]
        issues_by_type[issue_type].append(issue)

    # Generate sections for each issue type
    for issue_type in sorted(issues_by_type.keys()):
        type_emoji = get_issue_type_emoji(issue_type)
        md_content.append(f"### 🔸 {issue_type}")
        md_content.append("")

        type_issues = issues_by_type[issue_type]

        for issue in type_issues:
            # Use the shared function to generate issue section
            story_subtasks = None
            if (
                issue["fields"]["issue_type"]["name"] == "Story"
                and issue["key"] in subtasks
            ):
                story_subtasks = subtasks[issue["key"]]

            md_content.extend(
                generate_issue_section(
                    issue,
                    jira_base_url,
                    include_subtasks=story_subtasks is not None,
                    subtasks=story_subtasks,
                )
            )

    # Footer
    md_content.extend(
        generate_export_footer(
            "Epic",
            epic_key,
            epic_summary,
            epic_data["total_issues"],
            epic_data.get("total_subtasks", 0),
            epic_data.get("download_timestamp", ""),
            jira_base_url,
        )
    )

    return "\n".join(md_content)


async def download_epic_issues(
    epic_key: str,
    output_dir: Optional[str] = None,
    output_filename: Optional[str] = None,
    include_subtasks: bool = True,
) -> EpicDownloadResult:
    """Download all issues from a Jira epic and save to Markdown.

    Args:
        epic_key: Epic key (e.g., 'PROJ-123')
        output_dir: Output directory for the Markdown file
        output_filename: Custom filename for the output file
        include_subtasks: Whether to fetch sub-tasks for stories

    Returns:
        EpicDownloadResult with download information
    """
    # Setup output directory
    if output_dir is None:
        output_dir = settings().output_dir
    ensure_directory_exists(output_dir)

    # Generate filename if not provided
    if output_filename is None:
        base_filename = generate_timestamp_filename(f"epic_{epic_key}")
        output_filename = base_filename.replace(".json", ".md")

    output_path = Path(output_dir) / output_filename

    logger.info(f"Starting download of epic {epic_key}")
    logger.info(f"Output will be saved to: {output_path}")

    async with JiraClient() as jira:
        try:
            # Get epic information
            logger.info("Fetching epic information...")
            epic_info = await jira.get_epic_info(epic_key)
            logger.info(f"Epic: {epic_info.key} - {epic_info.fields.summary}")

            # Get all issues in the epic
            logger.info("Fetching all issues in the epic...")
            issues = await jira.get_epic_issues(epic_key)

            # Fetch sub-tasks for stories in the epic (if requested)
            subtasks_by_story = {}
            total_subtasks = 0

            if include_subtasks:
                logger.info("Fetching sub-tasks for stories in the epic...")
                for issue in issues:
                    if issue.fields.issue_type.name == "Story":
                        logger.info(f"Fetching sub-tasks for story {issue.key}...")
                        story_subtasks = await jira.get_story_subtasks(issue.key)
                        if story_subtasks:
                            subtasks_by_story[issue.key] = story_subtasks
                            total_subtasks += len(story_subtasks)
                            logger.info(
                                f"Found {len(story_subtasks)} sub-tasks for story {issue.key}"
                            )

                logger.info(f"Total sub-tasks found: {total_subtasks}")
            else:
                logger.info("Skipping sub-task fetching as requested")

            # Create result object with readable issue data
            logger.info("Processing issues and extracting descriptions...")
            readable_issues = []
            for issue in issues:
                issue_data = issue.model_dump()
                # Extract readable text from description
                if issue_data["fields"]["description"]:
                    issue_data["fields"]["description_text"] = extract_text_from_adf(
                        issue_data["fields"]["description"]
                    )
                readable_issues.append(issue_data)

            # Process sub-tasks and extract descriptions (if we have sub-tasks)
            readable_subtasks_by_story = {}
            if include_subtasks and subtasks_by_story:
                logger.info("Processing sub-tasks and extracting descriptions...")
                for story_key, story_subtasks in subtasks_by_story.items():
                    readable_subtasks = []
                    for subtask in story_subtasks:
                        subtask_data = subtask.model_dump()
                        # Extract readable text from description
                        if subtask_data["fields"]["description"]:
                            subtask_data["fields"]["description_text"] = (
                                extract_text_from_adf(
                                    subtask_data["fields"]["description"]
                                )
                            )
                        readable_subtasks.append(subtask_data)
                    readable_subtasks_by_story[story_key] = readable_subtasks

            # Create epic data structure
            epic_data = {
                "epic_key": epic_key,
                "epic_summary": epic_info.fields.summary,
                "total_issues": len(issues),
                "total_subtasks": total_subtasks,
                "issues": readable_issues,
                "subtasks": readable_subtasks_by_story,
                "download_timestamp": datetime.now().isoformat(),
            }

            # Generate markdown content
            logger.info("Generating markdown content...")
            markdown_content = create_markdown_from_epic_data(epic_data)

            # Save markdown to file
            logger.info("Saving markdown file...")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            # Create result object for return
            result = EpicDownloadResult(
                epic_key=epic_key,
                epic_summary=epic_info.fields.summary,
                total_issues=len(issues),
                total_subtasks=total_subtasks,
                issues=issues,
                subtasks=subtasks_by_story,
                download_timestamp=datetime.now(),
                output_file=str(output_path),
            )

            # Log success information
            file_size = get_file_size(str(output_path))
            logger.info(
                f"Successfully downloaded {len(issues)} issues and {total_subtasks} sub-tasks"
            )
            logger.info(f"Markdown file: {output_path} ({format_file_size(file_size)})")

            return result

        except Exception as e:
            logger.error(f"Error downloading epic issues: {str(e)}")
            raise


@click.command()
@click.argument("epic_key", type=str)
@click.option(
    "--output-dir",
    "-o",
    default=None,
    help="Output directory for the Markdown file",
)
@click.option(
    "--output-filename",
    "-f",
    default=None,
    help="Custom filename for the output file (should end in .md)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--no-subtasks",
    is_flag=True,
    help="Skip fetching sub-tasks for stories (faster execution)",
)
def main(
    epic_key: str,
    output_dir: Optional[str],
    output_filename: Optional[str],
    verbose: bool,
    no_subtasks: bool,
) -> None:
    """Download all issues from a Jira epic and save them to Markdown.

    EPIC_KEY: The Jira epic key (e.g., 'PROJ-123')

    Examples:
        python download_epic_issues.py PROJ-123
        python download_epic_issues.py PROJ-123 -o ./exports
        python download_epic_issues.py PROJ-123 -f my_epic_issues.md
        python download_epic_issues.py PROJ-123 --no-subtasks
    """
    setup_logging(verbose)
    validate_settings(verbose)

    # Run the download
    try:
        result = asyncio.run(
            download_epic_issues(
                epic_key=epic_key,
                output_dir=output_dir,
                output_filename=output_filename,
                include_subtasks=not no_subtasks,
            )
        )

        print_success_message(
            "Epic",
            result.epic_key,
            result.epic_summary,
            result.total_issues,
            result.total_subtasks,
            result.output_file,
        )

    except Exception as e:
        handle_download_error(e, "epic issues")


if __name__ == "__main__":
    main()
