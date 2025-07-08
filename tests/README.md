# Test Documentation

## Overview

This directory contains comprehensive unit tests for the Jirabot project, specifically focusing on the `download_story_subtasks.py` script.

## Test Files

### `test_download_story_subtasks.py`

Comprehensive test suite for the story download functionality with **99% code coverage**.

#### Test Classes and Coverage:

1. **TestCreateMarkdownFromStoryData**
   - Tests the markdown generation function
   - Covers scenarios with and without subtasks
   - Tests custom Jira URLs
   - Tests stories without descriptions
   - Validates proper markdown structure and content

2. **TestDownloadStorySubtasks**
   - Tests the main async download function
   - Covers successful downloads
   - Tests default parameter handling
   - Tests error handling (Jira API failures)
   - Tests scenarios with no subtasks
   - Uses proper mocking of external dependencies

3. **TestMainFunction**
   - Tests the CLI interface
   - Covers successful execution
   - Tests error handling
   - Tests all command-line options (verbose, custom output dir/filename)
   - Uses Click's CliRunner for realistic CLI testing

4. **TestIntegration**
   - End-to-end integration test
   - Tests the complete download flow
   - Validates file creation and content
   - Ensures proper integration between all components

## Test Features

### Mocking Strategy
- **JiraClient**: Mocked to avoid real API calls
- **File I/O**: Mocked using `mock_open()` for controlled testing
- **Pydantic Models**: Properly structured fixtures matching real model requirements
- **External Dependencies**: All external calls are mocked

### Test Data
- Realistic test fixtures with proper Jira field structures
- Complete mock objects with all required Pydantic model fields
- Covers various issue types, statuses, and assignees

### Async Testing
- Uses `pytest-asyncio` for proper async function testing
- Properly handles async context managers
- Tests both successful and error scenarios

## Running the Tests

### Prerequisites
```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio pytest-cov
```

### Run Tests
```bash
# Run all tests
python -m pytest tests/test_download_story_subtasks.py -v

# Run with coverage
python -m pytest tests/test_download_story_subtasks.py --cov=download_story_subtasks --cov-report=term-missing

# Run specific test class
python -m pytest tests/test_download_story_subtasks.py::TestCreateMarkdownFromStoryData -v
```

## Configuration

The tests use the `pytest.ini` configuration file which includes:
- Coverage settings with 80% minimum threshold
- Async mode configuration
- Warning filters
- Test discovery patterns

## Test Quality Metrics

- **Code Coverage**: 99%
- **Test Count**: 12 comprehensive tests
- **Assertions**: Multiple assertions per test validating different aspects
- **Mocking**: Comprehensive mocking of all external dependencies
- **Error Coverage**: Tests both success and failure scenarios

## Best Practices Implemented

1. **Isolation**: Each test is independent with proper setup/teardown
2. **Realistic Data**: Test fixtures match production data structures
3. **Edge Cases**: Tests cover empty data, missing fields, and error conditions
4. **Performance**: Tests run quickly due to proper mocking
5. **Maintainability**: Clear test names and comprehensive docstrings
6. **Async Safety**: Proper handling of async/await patterns in tests
