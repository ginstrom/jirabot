# Jirabot

A Python bot for interacting with Jira APIs and potentially integrating with other services like Slack.

## Project Structure

```
jirabot/
├── src/
│   ├── api/          # API related code (Jira, Slack, etc.)
│   ├── utils/        # Utility functions
│   ├── models/       # Data models and schemas
│   └── config/       # Configuration files
├── tests/            # Test files using pytest
├── docs/             # Documentation
├── requirements.txt  # Python dependencies
├── pyproject.toml    # Project configuration
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd jirabot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

### Configuration

1. Set up your environment variables in `.env`:
   ```
   JIRA_URL=your-jira-instance-url
   JIRA_USERNAME=your-username
   JIRA_API_TOKEN=your-api-token
   SLACK_BOT_TOKEN=your-slack-bot-token
   SLACK_SIGNING_SECRET=your-slack-signing-secret
   ```

2. Configure any additional API keys as needed

### Development

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python -m src.main

# Run tests
pytest

# Run tests with coverage
pytest --cov=src

# Format code
black src tests

# Lint code
flake8 src tests

# Type checking
mypy src
```

## Features

- Jira API integration with async support
- Slack bot integration (optional)
- RESTful API endpoints
- Comprehensive error handling and logging
- Rate limiting with backoff
- Unit tests with pytest
- Type hints for better code clarity
- Pydantic models for data validation
- Epic and Story export tools

## Scripts

### Download Epic Issues

Downloads all issues from a Jira epic and saves them to a Markdown file with rich formatting. **Now also includes sub-tasks of stories within the epic!**

```bash
# Download all issues from an epic (including sub-tasks of stories)
python download_epic_issues.py PROJ-123

# Specify output directory
python download_epic_issues.py PROJ-123 -o ./exports

# Custom filename
python download_epic_issues.py PROJ-123 -f my_epic_issues.md

# Skip sub-tasks for faster execution
python download_epic_issues.py PROJ-123 --no-subtasks

# Verbose logging
python download_epic_issues.py PROJ-123 -v
```

**Enhanced Features:**
- 📋 Automatically fetches sub-tasks for all stories in the epic
- 🔗 Sub-tasks are displayed under their parent stories
- 📊 Statistics include both main issues and sub-tasks
- ⚡ Concurrent fetching for better performance

### Download Story Sub-tasks

Downloads a Jira story and its sub-tasks and saves them to a Markdown file with rich formatting.

```bash
# Download a story and its sub-tasks
python download_story_subtasks.py ELIZA-1913

# Specify output directory
python download_story_subtasks.py ELIZA-1913 -o ./exports

# Custom filename
python download_story_subtasks.py ELIZA-1913 -f my_story_subtasks.md

# Verbose logging
python download_story_subtasks.py ELIZA-1913 -v
```

Both scripts generate:
- 📊 Summary statistics with emojis
- 📋 Detailed issue information
- 🔗 Clickable links to Jira tickets
- 📝 Formatted descriptions with automatic ticket linking
- 🏷️ Labels, priorities, and assignee information

## Development Tools

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing
- **Pydantic** for data validation
- **FastAPI** for web framework (if applicable)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Set up your development environment with `pip install -r requirements-dev.txt`
4. Make your changes following PEP 8 style guidelines
5. Add tests for new functionality
6. Run the test suite and ensure all tests pass
7. Format your code with `black` and check with `flake8`
8. Submit a pull request

## License

This project is licensed under the MIT License.
