#!/usr/bin/env python3
"""Script to download a Jira story and its sub-tasks and save them to Markdown."""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import defaultdict

import click
from dotenv import load_dotenv

from src.api.jira_client import JiraClient
from src.config.settings import settings
from src.models.jira_models import StoryDownloadResult
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
    format_issue_details_table,
    format_description_blockquote,
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


def create_markdown_from_story_data(
    story_data, jira_base_url="https://mercari.atlassian.net"
):
    """Convert story data to markdown format."""

    # Start building markdown content
    md_content = []

    # Title and Story Information
    story_key = story_data["story_key"]
    story_summary = story_data["story_summary"]
    md_content.append(
        f"# Story: [{story_key}]({jira_base_url}/browse/{story_key}) - {story_summary}"
    )
    md_content.append("")
    md_content.append(
        f"**Download Date:** {format_date(story_data.get('download_timestamp', ''))}"
    )
    md_content.append(f"**Total Sub-tasks:** {story_data['total_subtasks']}")
    md_content.append("")

    # Story Details
    story_info = story_data["story_issue"]
    story_fields = story_info["fields"]

    # Story information section
    md_content.append("## 📖 Story Information")
    md_content.append("")

    # Use shared function for story details table
    md_content.extend(format_issue_details_table(story_fields))
    md_content.append("")

    # Story Description
    if story_fields.get("description_text"):
        md_content.append("### 📝 Story Description")
        md_content.append("")
        md_content.extend(
            format_description_blockquote(
                story_fields["description_text"], jira_base_url
            )
        )
        md_content.append("")

    # Analyze sub-tasks for summary stats
    subtasks = story_data["subtasks"]
    if subtasks:
        # Generate summary statistics for subtasks
        stats = generate_summary_statistics(subtasks)

        # Summary Statistics
        md_content.append("## 📊 Sub-tasks Summary Statistics")
        md_content.append("")
        md_content.extend(generate_statistics_markdown(stats))

        # Table of Contents
        md_content.append("## 📋 Table of Contents")
        md_content.append("")
        md_content.append("- [Story Information](#📖-story-information)")
        md_content.append(
            "- [Sub-tasks Summary Statistics](#📊-sub-tasks-summary-statistics)"
        )
        md_content.append("- [All Sub-tasks](#📋-all-sub-tasks)")

        # Group sub-tasks by type for TOC
        for issue_type in sorted(stats["issue_types"].keys()):
            anchor = issue_type.lower().replace(" ", "-").replace("/", "")
            md_content.append(f"  - [{issue_type}](#🔸-{anchor})")
        md_content.append("")

        # All Sub-tasks Section
        md_content.append("## 📋 All Sub-tasks")
        md_content.append("")

        # Group sub-tasks by type
        subtasks_by_type = defaultdict(list)
        for subtask in subtasks:
            issue_type = subtask["fields"]["issue_type"]["name"]
            subtasks_by_type[issue_type].append(subtask)

        # Generate sections for each issue type
        for issue_type in sorted(subtasks_by_type.keys()):
            type_emoji = get_issue_type_emoji(issue_type)
            md_content.append(f"### 🔸 {issue_type}")
            md_content.append("")

            type_subtasks = subtasks_by_type[issue_type]

            for subtask in type_subtasks:
                # Use the shared function to generate issue section
                md_content.extend(
                    generate_issue_section(
                        subtask,
                        jira_base_url,
                        include_subtasks=False,
                        subtasks=None,
                    )
                )

    else:
        md_content.append("## 📋 Sub-tasks")
        md_content.append("")
        md_content.append("No sub-tasks found for this story.")
        md_content.append("")

    # Footer
    md_content.extend(
        generate_export_footer(
            "Story",
            story_key,
            story_summary,
            len(subtasks),
            len(subtasks),
            story_data.get("download_timestamp", ""),
            jira_base_url,
        )
    )

    return "\n".join(md_content)


async def download_story_subtasks(
    story_key: str,
    output_dir: Optional[str] = None,
    output_filename: Optional[str] = None,
) -> StoryDownloadResult:
    """Download a Jira story and its sub-tasks and save to Markdown.

    Args:
        story_key: Story key (e.g., 'PROJ-123')
        output_dir: Output directory for the Markdown file
        output_filename: Custom filename for the output file

    Returns:
        StoryDownloadResult with download information
    """
    # Setup output directory
    if output_dir is None:
        output_dir = settings().output_dir
    ensure_directory_exists(output_dir)

    # Generate filename if not provided
    if output_filename is None:
        base_filename = generate_timestamp_filename(f"story_{story_key}")
        output_filename = base_filename.replace(".json", ".md")

    output_path = Path(output_dir) / output_filename

    logger.info(f"Starting download of story {story_key}")
    logger.info(f"Output will be saved to: {output_path}")

    async with JiraClient() as jira:
        try:
            # Get story information
            logger.info("Fetching story information...")
            story_info = await jira.get_story_info(story_key)
            logger.info(f"Story: {story_info.key} - {story_info.fields.summary}")

            # Get all sub-tasks for the story
            logger.info("Fetching all sub-tasks for the story...")
            subtasks = await jira.get_story_subtasks(story_key)

            # Create result object with readable issue data
            logger.info("Processing story and sub-tasks and extracting descriptions...")

            # Process story info
            story_data = story_info.model_dump()
            if story_data["fields"]["description"]:
                story_data["fields"]["description_text"] = extract_text_from_adf(
                    story_data["fields"]["description"]
                )

            # Process sub-tasks
            readable_subtasks = []
            for subtask in subtasks:
                subtask_data = subtask.model_dump()
                # Extract readable text from description
                if subtask_data["fields"]["description"]:
                    subtask_data["fields"]["description_text"] = extract_text_from_adf(
                        subtask_data["fields"]["description"]
                    )
                readable_subtasks.append(subtask_data)

            # Create story data structure
            story_data_export = {
                "story_key": story_key,
                "story_summary": story_info.fields.summary,
                "total_subtasks": len(subtasks),
                "story_issue": story_data,
                "subtasks": readable_subtasks,
                "download_timestamp": datetime.now().isoformat(),
            }

            # Generate markdown content
            logger.info("Generating markdown content...")
            markdown_content = create_markdown_from_story_data(story_data_export)

            # Save markdown to file
            logger.info("Saving markdown file...")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            # Create result object for return
            result = StoryDownloadResult(
                story_key=story_key,
                story_summary=story_info.fields.summary,
                total_subtasks=len(subtasks),
                story_issue=story_info,
                subtasks=subtasks,
                download_timestamp=datetime.now(),
                output_file=str(output_path),
            )

            # Log success information
            file_size = get_file_size(str(output_path))
            logger.info(f"Successfully downloaded story with {len(subtasks)} sub-tasks")
            logger.info(f"Markdown file: {output_path} ({format_file_size(file_size)})")

            return result

        except Exception as e:
            logger.error(f"Error downloading story and sub-tasks: {str(e)}")
            raise


@click.command()
@click.argument("story_key", type=str)
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
def main(
    story_key: str,
    output_dir: Optional[str],
    output_filename: Optional[str],
    verbose: bool,
) -> None:
    """Download a Jira story and its sub-tasks and save them to Markdown.

    STORY_KEY: The Jira story key (e.g., 'PROJ-123')

    Examples:
        python download_story_subtasks.py ELIZA-1913
        python download_story_subtasks.py ELIZA-1913 -o ./exports
        python download_story_subtasks.py ELIZA-1913 -f my_story_subtasks.md
    """
    setup_logging(verbose)
    validate_settings(verbose)

    # Run the download
    try:
        result = asyncio.run(
            download_story_subtasks(
                story_key=story_key,
                output_dir=output_dir,
                output_filename=output_filename,
            )
        )

        print_success_message(
            "Story",
            result.story_key,
            result.story_summary,
            result.total_subtasks,
            result.total_subtasks,
            result.output_file,
        )

    except Exception as e:
        handle_download_error(e, "story and sub-tasks")


if __name__ == "__main__":
    main()
