# Jirabot Setup Guide

## Prerequisites

- Python 3.8 or higher
- Jira instance with API access
- Jira API token

## Installation

1. Clone the repository and navigate to the project directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Jira Configuration
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token

# Application Configuration
LOG_LEVEL=INFO
DEBUG=false
ENVIRONMENT=development
OUTPUT_DIR=output
```

### Getting Your Jira API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a descriptive name
4. Copy the token and add it to your `.env` file

## Usage

### Download Epic Issues

Use the `download_epic_issues.py` script to download all issues from a Jira epic:

```bash
# Basic usage
python download_epic_issues.py PROJ-123

# Custom output directory
python download_epic_issues.py PROJ-123 -o ./exports

# Custom filename
python download_epic_issues.py PROJ-123 -f my_epic_issues.json

# Verbose logging
python download_epic_issues.py PROJ-123 -v
```

### Script Options

- `EPIC_KEY`: The Jira epic key (e.g., 'PROJ-123')
- `--output-dir, -o`: Output directory for the JSON file
- `--output-filename, -f`: Custom filename for the output file
- `--verbose, -v`: Enable verbose logging

### Output

The script will create a JSON file containing:
- Epic information (key, summary)
- All issues in the epic with full details
- Download timestamp
- Total issue count

Example output structure:
```json
{
  "epic_key": "PROJ-123",
  "epic_summary": "Epic Summary",
  "total_issues": 15,
  "issues": [
    {
      "id": "12345",
      "key": "PROJ-124",
      "fields": {
        "summary": "Issue Summary",
        "status": {...},
        "assignee": {...},
        ...
      }
    }
  ],
  "download_timestamp": "2024-01-15T10:30:00",
  "output_file": "output/epic_PROJ-123_20240115_103000.json"
}
```

## Features

- **Async/Await**: Fast, non-blocking API calls
- **Rate Limiting**: Respects Jira API rate limits
- **Error Handling**: Comprehensive error handling and logging
- **Type Safety**: Full type hints and Pydantic models
- **Pagination**: Handles large epics with automatic pagination
- **Logging**: Detailed logging with configurable levels

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check your Jira URL, username, and API token
2. **Epic Not Found**: Verify the epic key exists and you have access
3. **Rate Limiting**: The script includes rate limiting, but you can adjust it in the JiraClient
4. **Connection Issues**: Check your network connection and Jira instance availability

### Logs

The script creates a `jirabot.log` file with detailed logging information. Use the `-v` flag for verbose output.

## Next Steps

This script provides a foundation for more advanced Jira automation. You can extend it to:
- Download multiple epics at once
- Filter issues by specific criteria
- Export to different formats (CSV, Excel)
- Integrate with Slack or other tools
- Schedule automated downloads
