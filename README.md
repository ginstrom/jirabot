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

#### Setting Up Development Environment

```bash
# Activate virtual environment (ALWAYS DO THIS FIRST)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

#### Development Workflow

##### 1. Testing (99% Coverage Achieved!)

```bash
# Run all tests with coverage
python -m pytest tests/ --cov=src --cov=download_story_subtasks --cov=download_epic_issues --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_download_story_subtasks.py -v

# Run specific test class
python -m pytest tests/test_download_story_subtasks.py::TestCreateMarkdownFromStoryData -v

# Run tests in parallel (if installed pytest-xdist)
python -m pytest tests/ -n auto
```

**Test Configuration:**
- Minimum 80% coverage requirement (currently at 99%)
- Async testing with `pytest-asyncio`
- Comprehensive mocking of external dependencies
- Integration tests for end-to-end workflows

##### 2. Code Quality

```bash
# Format code
black src tests *.py

# Lint code
flake8 src tests *.py

# Type checking
mypy src *.py

# Run all quality checks
black src tests *.py && flake8 src tests *.py && mypy src *.py
```

##### 3. Git Workflow

**Before making changes:**
```bash
# Create feature branch
git checkout -b feature/your-feature-name
```

**After making changes:**
```bash
# 1. Run tests first
source venv/bin/activate
python -m pytest tests/ --cov=src --cov-report=term-missing

# 2. Check code quality
black src tests *.py
flake8 src tests *.py

# 3. Stage and commit in logical groups
git add [related-files]
git commit -m "type: brief description

- Detailed bullet point 1
- Detailed bullet point 2"

# 4. Push changes
git push origin feature/your-feature-name
```

**Commit Types:**
- `feat:` - New features
- `fix:` - Bug fixes
- `test:` - Adding or updating tests
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

##### 4. Running the Application

```bash
# Download epic with all sub-tasks
python download_epic_issues.py PROJ-123

# Download story with sub-tasks
python download_story_subtasks.py PROJ-123

# With verbose logging for debugging
python download_story_subtasks.py PROJ-123 -v
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

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines including:

- 🛠️ Development environment setup
- 🧪 Testing requirements (99% coverage!)
- 📝 Git commit guidelines and workflow
- 🔍 Code quality standards
- 📋 Pull request process

**Quick Start:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. **Always activate venv**: `source venv/bin/activate`
4. Make changes following our coding standards
5. **Run tests**: `python -m pytest tests/ --cov=src --cov-report=term-missing`
6. **Check code quality**: `black src tests *.py && flake8 src tests *.py`
7. Commit in logical groups with clear messages
8. Submit a pull request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for complete details.

## License

This project is licensed under the MIT License.
