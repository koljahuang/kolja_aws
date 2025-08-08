#!/usr/bin/env python3
"""
Integration test runner for shell profile switcher

This script runs all integration tests and provides comprehensive reporting
on the test results, including performance metrics and coverage information.
"""

import os
import sys
import time
import subprocess
from pathlib import Path


def run_test_suite(test_pattern: str = None, verbose: bool = False) -> bool:
    """
    Run the integration test suite
    
    Args:
        test_pattern: Optional pattern to filter tests
        verbose: Enable verbose output
        
    Returns:
        True if all tests pass, False otherwise
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    # Add coverage reporting if pytest-cov is available
    try:
        import pytest_cov
        cmd.extend([
            '--cov=kolja_aws',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov'
        ])
    except ImportError:
        print("Note: pytest-cov not installed, skipping coverage reporting")
    
    # Add test pattern if specified
    if test_pattern:
        cmd.append(f'-k={test_pattern}')
    
    # Add test directories
    cmd.extend([
        'tests/test_integration_e2e.py',
        'tests/test_integration_comprehensive.py',
        'tests/test_performance.py',
        'tests/test_integration.py'
    ])
    
    print("Running integration test suite...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        end_time = time.time()
        
        print("-" * 60)
        print(f"Test execution completed in {end_time - start_time:.2f} seconds")
        
        if result.returncode == 0:
            print("✅ All integration tests passed!")
            return True
        else:
            print("❌ Some integration tests failed!")
            return False
            
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def run_specific_test_categories():
    """Run specific categories of integration tests"""
    categories = {
        'e2e': 'tests/test_integration_e2e.py',
        'comprehensive': 'tests/test_integration_comprehensive.py',
        'performance': 'tests/test_performance.py',
        'integration': 'tests/test_integration.py'
    }
    
    results = {}
    
    for category, test_file in categories.items():
        print(f"\n{'='*60}")
        print(f"Running {category.upper()} tests...")
        print(f"{'='*60}")
        
        cmd = ['python', '-m', 'pytest', '-v', test_file]
        
        # Add coverage if available
        try:
            import pytest_cov
            cmd.extend(['--cov=kolja_aws', '--cov-report=term-missing'])
        except ImportError:
            pass
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=False, text=True)
        end_time = time.time()
        
        results[category] = {
            'passed': result.returncode == 0,
            'duration': end_time - start_time
        }
        
        status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
        print(f"\n{category.upper()} tests: {status} ({results[category]['duration']:.2f}s)")
    
    # Summary
    print(f"\n{'='*60}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    
    total_duration = sum(r['duration'] for r in results.values())
    passed_count = sum(1 for r in results.values() if r['passed'])
    total_count = len(results)
    
    for category, result in results.items():
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"{category.upper():12} {status:10} ({result['duration']:.2f}s)")
    
    print(f"\nOverall: {passed_count}/{total_count} test categories passed")
    print(f"Total execution time: {total_duration:.2f} seconds")
    
    return passed_count == total_count


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run integration tests for shell profile switcher')
    parser.add_argument('--pattern', '-k', help='Test pattern to filter tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--categories', '-c', action='store_true', 
                       help='Run tests by categories with detailed reporting')
    
    args = parser.parse_args()
    
    if args.categories:
        success = run_specific_test_categories()
    else:
        success = run_test_suite(args.pattern, args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()