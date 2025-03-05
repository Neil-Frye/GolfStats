#!/usr/bin/env python
"""
Run tests for GolfStats application.

This script allows running different types of tests for the GolfStats application.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run unit tests only
    python run_tests.py --integration # Run integration tests only
"""
import os
import sys
import unittest
import argparse

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def run_all_tests():
    """Run all tests in the tests directory."""
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def run_unit_tests():
    """Run unit tests only."""
    test_suite = unittest.TestSuite()
    
    # Manually load the test_app.py module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "test_app", 
        os.path.join(project_root, "tests", "test_app.py")
    )
    test_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_app)
    
    # Add all tests from the TestApp class
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
        test_app.TestApp
    ))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests only."""
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Manually load the test_integration.py module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "test_integration", 
        os.path.join(project_root, "tests", "test_integration.py")
    )
    test_integration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_integration)
    
    # Add all tests from the TestGolfStatsIntegration class
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
        test_integration.TestGolfStatsIntegration
    ))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def run_with_coverage():
    """Run all tests with coverage."""
    try:
        import coverage
    except ImportError:
        print("Coverage package not installed. Run: pip install pytest-cov")
        return False
    
    cov = coverage.Coverage(
        source=["backend"],
        omit=["*/__pycache__/*", "*/test_*", "*/venv/*"]
    )
    cov.start()
    
    # Run all tests
    success = run_all_tests()
    
    cov.stop()
    cov.save()
    
    # Generate console report
    print("\nCoverage Report:")
    cov.report()
    
    # Generate HTML report
    reports_dir = os.path.join(project_root, 'reports', 'coverage')
    os.makedirs(reports_dir, exist_ok=True)
    cov.html_report(directory=reports_dir)
    print(f"\nHTML coverage report saved to: {reports_dir}")
    
    return success

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run GolfStats tests")
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage')
    args = parser.parse_args()
    
    if args.coverage:
        success = run_with_coverage()
    elif args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)