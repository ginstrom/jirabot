"""CLI helper utilities for Jira download scripts."""

import logging
import sys
from typing import Optional

from ..config.settings import settings


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.

    Args:
        verbose: Whether to enable verbose logging
    """
    # Configure logging (will be configured properly in main function)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("jirabot.log"),
        ],
    )

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


def validate_settings(verbose: bool = False) -> None:
    """Validate required settings and configure logging.

    Args:
        verbose: Whether verbose logging is enabled

    Raises:
        SystemExit: If settings are invalid
    """
    logger = logging.getLogger(__name__)

    try:
        if not settings().jira_url:
            raise ValueError("JIRA_URL environment variable is required")
        if not settings().jira_username:
            raise ValueError("JIRA_USERNAME environment variable is required")
        if not settings().jira_api_token:
            raise ValueError("JIRA_API_TOKEN environment variable is required")

        # Configure logging level from settings
        if not verbose:
            logging.getLogger().setLevel(getattr(logging, settings().log_level.upper()))

    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        logger.error(
            "Please check your .env file and ensure all required variables are set"
        )
        sys.exit(1)


def print_success_message(
    item_type: str,
    item_key: str,
    item_summary: str,
    total_items: int,
    total_subtasks: int,
    output_file: str,
) -> None:
    """Print success message after download completion.

    Args:
        item_type: Type of item (Epic, Story, etc.)
        item_key: Item key (e.g., PROJ-123)
        item_summary: Item summary
        total_items: Total number of items downloaded
        total_subtasks: Total number of subtasks downloaded
        output_file: Path to output file
    """
    print(f"\n✅ Success!")
    print(f"{item_type}: {item_key} - {item_summary}")

    if item_type.lower() == "epic":
        print(f"Issues downloaded: {total_items}")
        print(f"Sub-tasks downloaded: {total_subtasks}")
    elif item_type.lower() == "story":
        print(f"Sub-tasks downloaded: {total_subtasks}")

    print(f"Markdown file: {output_file}")


def handle_download_error(error: Exception, item_type: str) -> None:
    """Handle download errors and exit.

    Args:
        error: Exception that occurred
        item_type: Type of item being downloaded
    """
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to download {item_type.lower()}: {str(error)}")
    sys.exit(1)
