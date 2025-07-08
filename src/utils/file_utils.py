"""File utility functions for the jirabot application."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

import logging

logger = logging.getLogger(__name__)


def ensure_directory_exists(directory: str) -> None:
    """Ensure that a directory exists, creating it if necessary.

    Args:
        directory: Directory path to create
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {directory}")


def save_json(data: Any, file_path: str, indent: int = 2) -> None:
    """Save data to a JSON file with proper formatting.

    Args:
        data: Data to save (must be JSON serializable)
        file_path: Path to save the file
        indent: JSON indentation level
    """
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

    logger.info(f"Saved JSON data to {file_path}")


def load_json(file_path: str) -> Any:
    """Load data from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Loaded data

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.debug(f"Loaded JSON data from {file_path}")
    return data


def generate_timestamp_filename(prefix: str, suffix: str = "json") -> str:
    """Generate a filename with timestamp.

    Args:
        prefix: Filename prefix
        suffix: File extension (without dot)

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{suffix}"


def get_file_size(file_path: str) -> int:
    """Get file size in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def extract_text_from_adf(content: Union[str, Dict[str, Any], None]) -> str:
    """
    Extract plain text from Atlassian Document Format (ADF) content.

    Args:
        content: ADF content or plain string

    Returns:
        Plain text string
    """
    if content is None:
        return ""

    if isinstance(content, str):
        return content

    if not isinstance(content, dict):
        return str(content)

    # Handle ADF format
    if content.get("type") == "doc" and "content" in content:
        text_parts = []
        _extract_text_recursive(content["content"], text_parts)
        return " ".join(text_parts).strip()

    return str(content)


def _extract_text_recursive(
    content: List[Dict[str, Any]], text_parts: List[str]
) -> None:
    """
    Recursively extract text from ADF content structure.

    Args:
        content: ADF content array
        text_parts: List to append text parts to
    """
    for item in content:
        if item.get("type") == "text" and "text" in item:
            text_parts.append(item["text"])
        elif item.get("type") == "hardBreak":
            text_parts.append("\n")
        elif "content" in item:
            _extract_text_recursive(item["content"], text_parts)
