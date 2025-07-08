# Contributing to Jirabot

Thank you for your interest in contributing to Jirabot! This guide will help you set up your development environment and understand our development workflow.

## Development Environment Setup

### Prerequisites

- Python 3.8+
- Git
- GitHub account

### Initial Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/jirabot.git
cd jirabot

# 3. Add upstream remote
git remote add upstream https://github.com/ginstrom/jirabot.git

# 4. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Set up environment variables
cp env_template.txt .env
# Edit .env with your Jira credentials
```

## Development Workflow

### 🚨 **CRITICAL: Always Use Virtual Environment**

**Before ANY development work:**
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1. Creating a Feature Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create and switch to feature branch
git checkout -b feature/your-feature-name
# OR for bug fixes:
git checkout -b fix/issue-description
```

### 2. Making Changes

Follow our coding standards:
- Use Python 3.8+ features
- Follow PEP 8 style guidelines
- Use type hints for better code clarity
- Add docstrings (Google or NumPy style)
- Use meaningful variable and function names
- Prefer async/await for I/O operations

### 3. Testing (MANDATORY - 99% Coverage Required!)

#### Running Tests

```bash
# ALWAYS activate venv first!
source venv/bin/activate

# Run all tests with coverage
python -m pytest tests/ --cov=src --cov=download_story_subtasks --cov=download_epic_issues --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_download_story_subtasks.py -v

# Run specific test class
python -m pytest tests/test_download_story_subtasks.py::TestCreateMarkdownFromStoryData -v

# Generate HTML coverage report
python -m pytest tests/ --cov=src --cov-report=html
# View htmlcov/index.html in browser
```

#### Writing Tests

**Test Requirements:**
- ✅ Minimum 80% coverage (we currently have 99%)
- ✅ Test both success and error scenarios
- ✅ Use proper mocking for external dependencies
- ✅ Follow async testing patterns for async functions
- ✅ Use realistic test fixtures

**Test Structure Example:**
```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestYourFunction:
    """Test cases for your_function."""

    @pytest.fixture
    def sample_data(self):
        """Sample test data."""
        return {"key": "value"}

    def test_success_case(self, sample_data):
        """Test successful execution."""
        # Test implementation

    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async function."""
        # Async test implementation

    def test_error_handling(self):
        """Test error scenarios."""
        with pytest.raises(ExpectedError):
            # Test error case
```

### 4. Code Quality Checks

**Run BEFORE committing:**
```bash
# Format code
black src tests *.py

# Check linting
flake8 src tests *.py

# Type checking
mypy src *.py

# All quality checks in one command
black src tests *.py && flake8 src tests *.py && mypy src *.py
```

### 5. Git Commit Guidelines

#### Commit Message Format

```
type: brief description (50 chars or less)

- Detailed explanation point 1
- Detailed explanation point 2
- Reference any issues: #123
```

#### Commit Types

- `feat:` - New features
- `fix:` - Bug fixes
- `test:` - Adding or updating tests
- `docs:` - Documentation changes
- `refactor:` - Code refactoring without functionality changes
- `chore:` - Maintenance tasks, dependency updates
- `perf:` - Performance improvements
- `style:` - Code style changes (formatting, etc.)

#### Commit Process

```bash
# 1. ALWAYS run tests first
source venv/bin/activate
python -m pytest tests/ --cov=src --cov-report=term-missing

# 2. Check code quality
black src tests *.py
flake8 src tests *.py
mypy src *.py

# 3. Stage files in logical groups
git add [related-files]

# 4. Commit with descriptive message
git commit -m "feat: add story export with sub-tasks

- Add async function to download story and all sub-tasks
- Generate markdown with proper formatting and statistics
- Include comprehensive error handling and logging
- Add CLI interface with Click for user-friendly operation"

# 5. If adding tests, commit separately
git add tests/test_new_feature.py
git commit -m "test: add comprehensive tests for story export

- Add unit tests for markdown generation
- Add async tests for download functionality
- Add CLI tests using Click's test runner
- Achieve 99% code coverage"
```

### 6. Pushing and Pull Requests

```bash
# Push your feature branch
git push origin feature/your-feature-name

# Create pull request on GitHub with:
# - Clear description of changes
# - Link to any related issues
# - Screenshots if UI changes
# - Test results confirmation
```

## Testing Guidelines

### Test Categories

1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test component interactions
3. **CLI Tests** - Test command-line interfaces
4. **Async Tests** - Test async/await functions

### Mocking Best Practices

```python
# Mock external dependencies
@patch('module.external_api_call')
@patch('module.file_operations')
def test_function(mock_file, mock_api):
    # Setup mocks
    mock_api.return_value = expected_data
    mock_file.return_value = success_response

    # Test your function
    result = your_function()

    # Verify results and mock calls
    assert result == expected_result
    mock_api.assert_called_once_with(expected_args)
```

### Async Testing

```python
@pytest.mark.asyncio
async def test_async_function():
    with patch('module.AsyncClass') as mock_class:
        mock_instance = AsyncMock()
        mock_class.return_value.__aenter__.return_value = mock_instance

        result = await your_async_function()

        assert result == expected
```

## Project Structure for Contributors

```
jirabot/
├── src/
│   ├── api/              # API clients (Jira, etc.)
│   ├── config/           # Configuration management
│   ├── models/           # Pydantic data models
│   └── utils/            # Utility functions
├── tests/                # Test files
│   ├── test_*.py        # Unit tests
│   └── README.md        # Test documentation
├── download_*.py         # Main application scripts
├── pytest.ini           # Test configuration
├── requirements.txt      # Dependencies
└── README.md            # Project documentation
```

## Common Issues and Solutions

### Virtual Environment Issues
```bash
# If tests fail with import errors:
deactivate
source venv/bin/activate
pip install -r requirements.txt
```

### Coverage Issues
```bash
# If coverage is below 80%:
python -m pytest --cov=src --cov-report=html
# Check htmlcov/index.html to see uncovered lines
```

### Async Test Issues
```bash
# If async tests fail:
pip install pytest-asyncio
# Ensure tests use @pytest.mark.asyncio
```

## Code Review Process

1. **Automated Checks**: All tests must pass, coverage ≥80%
2. **Code Quality**: Black formatting, flake8 linting, mypy typing
3. **Manual Review**: Logic, design patterns, documentation
4. **Testing**: Reviewer may run tests locally

## Getting Help

- 📖 Check existing documentation
- 🔍 Search existing issues
- 💬 Open a new issue for questions
- 📧 Contact maintainers

## Release Process

1. All features merged to main
2. Version bump in pyproject.toml
3. Update CHANGELOG.md
4. Create release tag
5. Deploy (automated)

---

**Remember**: Quality over speed. Take time to write good tests and clear commit messages. Your future self (and other contributors) will thank you!
