# GolfStats Development Guide

## Build/Run Commands
- Install dependencies: `pip install -r backend/requirements.txt`
- Run backend server: `python backend/app.py`
- Run all tests: `python -m unittest discover tests`
- Run single test: `python -m unittest tests.test_app.TestApp.test_index`
- Lint code: `pylint backend tests`
- Type check: `mypy backend tests`

## Code Style Guidelines
- Follow PEP 8 standards with 79 character line limit
- Import order: standard library, third-party, local (absolute imports from root)
- Use snake_case for variables/functions, CamelCase for classes
- Include type hints for all function parameters and return values
- Use specific exceptions with appropriate logging
- Document all functions with docstrings (purpose, params, returns, errors)
- Keep functions small and focused on a single responsibility
- Prefer composition over inheritance

## Version Control
- Make small, frequent commits with descriptive messages
- Use the pattern: `git add . && git commit -m "Description" && git push origin master`

## Web Scraping
- Use Selenium or Pyppeteer for screen scraping Trackman, Arccos, SkyTrak
- Handle authentication and session management securely