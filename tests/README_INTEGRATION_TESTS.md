# GolfStats Integration Tests

This document describes the integration testing approach for the GolfStats application.

## Overview

Integration tests verify that different components of the application work together correctly. These tests validate end-to-end flows from a user logging in to data being scraped, stored, and displayed.

## Test Coverage

The integration tests cover the following flows:

1. **Authentication Flow**
   - User login
   - Session management
   - User information retrieval
   - Logout

2. **Data Retrieval Flow**
   - Listing golf rounds
   - Retrieving detailed round information with shots
   - Accessing user statistics

3. **ETL Processing Flow**
   - Extracting data from third-party sources (Trackman, Arccos, SkyTrak)
   - Transforming and storing data in the database
   - Integration between scrapers and storage components

4. **End-to-End User Flow**
   - Complete user journey from login to viewing statistics

## Setup

Before running integration tests, install the required dependencies:

```bash
# Install all dependencies
pip install -r requirements.txt
```

## Running Integration Tests

To run the integration tests:

```bash
# Run only integration tests
python run_tests.py --integration

# Run all tests including integration tests
python run_tests.py

# Run unit tests only
python run_tests.py --unit

# Run tests with coverage report
python run_tests.py --coverage
```

The coverage report will be generated in HTML format in the `reports/coverage` directory.

If you encounter any import errors, ensure all dependencies are installed and that your Python environment is properly configured.

## Test Architecture

The integration tests use:

1. **Mocking**: External dependencies (like third-party APIs) are mocked to ensure tests are reliable and don't make actual network calls
2. **Flask Test Client**: Tests use Flask's test client to simulate HTTP requests
3. **Patch Decorators**: Python's unittest.mock.patch is used to inject test doubles

## Adding New Integration Tests

When adding new integration tests:

1. Place them in the `tests/test_integration.py` file
2. Follow the existing pattern of mocking external dependencies
3. Ensure each test has a clear, specific purpose
4. Test realistic user flows

## Test Data

The tests use mock data that mimics the structure of actual application data:

- User credentials and profile information
- Golf round data with course information and scores
- Shot data with club selections and performance metrics
- Statistics summaries

## Troubleshooting

If integration tests are failing:

1. Check that all necessary mocks are in place
2. Verify that route paths match the actual application
3. Ensure test data structure matches what the application expects
4. Look for changes in the application's API contracts