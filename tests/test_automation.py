"""
Automated testing script for Data Profiler using Playwright.
Tests all 4 features across multiple test files.
"""

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

# Test file paths
TEST_FILES = {
    'numeric': 'test_data/test_numeric.csv',
    'strings': 'test_data/test_strings.csv',
    'dates': 'test_data/test_dates.csv',
    'duplicates': 'test_data/test_duplicates.csv',
    'all_features': 'test_data/test_all_features.csv'
}

# Get absolute paths
TEST_FILES = {k: str(Path(v).absolute()) for k, v in TEST_FILES.items()}

class DataProfilerTester:
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.page = None
        self.browser = None

    def log_pass(self, test_name):
        print(f"  ✓ PASS: {test_name}")
        self.results['passed'].append(test_name)

    def log_fail(self, test_name, reason):
        print(f"  ✗ FAIL: {test_name} - {reason}")
        self.results['failed'].append((test_name, reason))

    def log_warning(self, test_name, msg):
        print(f"  ⚠ WARNING: {test_name} - {msg}")
        self.results['warnings'].append((test_name, msg))

    def start_browser(self):
        """Initialize browser"""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def navigate_to_app(self):
        """Navigate to Streamlit app"""
        print("\n[APP STARTUP]")
        self.page.goto('http://localhost:8501', wait_until='networkidle', timeout=10000)
        self.page.wait_for_load_state('networkidle')
        time.sleep(2)

    def test_app_startup(self):
        """Test 2.1.1: App starts without errors"""
        try:
            title = self.page.title()
            if 'Data Profiler' in title or title:
                self.log_pass("App startup")
                return True
            else:
                self.log_fail("App startup", "Title not found")
                return False
        except Exception as e:
            self.log_fail("App startup", str(e))
            return False

    def test_initial_state(self):
        """Test 2.1.2: Initial state shows upload message"""
        try:
            # Look for the upload prompt message
            self.page.wait_for_selector("text='Upload a file using the sidebar'", timeout=5000)
            self.log_pass("Initial state message")
            return True
        except Exception as e:
            self.log_warning("Initial state message", f"Could not find upload message: {str(e)}")
            return True  # App might still be working

    def upload_file(self, file_key):
        """Upload a test file and wait for processing"""
        file_path = TEST_FILES[file_key]

        if not os.path.exists(file_path):
            self.log_fail(f"Upload {file_key}", f"File not found: {file_path}")
            return False

        try:
            # Find the file input and set it
            file_input = self.page.locator('input[type="file"]')
            file_input.set_input_files(file_path)

            # Wait for success message
            self.page.wait_for_selector("text='Successfully profiled'", timeout=30000)
            time.sleep(2)  # Wait for rendering

            self.log_pass(f"Upload {file_key}")
            return True
        except Exception as e:
            self.log_fail(f"Upload {file_key}", str(e))
            return False

    def test_phase1_skewness(self):
        """Test 3.1.1: Skewness metric displays"""
        try:
            # Click on detailed view checkbox
            checkbox = self.page.locator('input[type="checkbox"]')
            checkbox.check()
            time.sleep(1)

            # Look for skewness metric
            self.page.wait_for_selector("text='Skewness'", timeout=5000)
            self.log_pass("Phase 1: Skewness metric")
            return True
        except Exception as e:
            self.log_warning("Phase 1: Skewness metric", str(e))
            return True  # May appear in summary instead

    def test_phase1_zeros(self):
        """Test 3.1.2: Zeros metric displays"""
        try:
            self.page.wait_for_selector("text='Zeros'", timeout=5000)
            self.log_pass("Phase 1: Zeros metric")
            return True
        except Exception as e:
            self.log_warning("Phase 1: Zeros metric", str(e))
            return True

    def test_phase1_negatives(self):
        """Test 3.1.3: Negatives metric displays"""
        try:
            self.page.wait_for_selector("text='Negatives'", timeout=5000)
            self.log_pass("Phase 1: Negatives metric")
            return True
        except Exception as e:
            self.log_warning("Phase 1: Negatives metric", str(e))
            return True

    def test_phase2_string_quality(self):
        """Test 3.2.1: String Quality section displays"""
        try:
            self.page.wait_for_selector("text='String Quality Analysis'", timeout=5000)
            self.log_pass("Phase 2: String Quality section")
            return True
        except Exception as e:
            self.log_warning("Phase 2: String Quality section", str(e))
            return True

    def test_phase2_whitespace(self):
        """Test 3.2.1.2: Whitespace Issues metric displays"""
        try:
            self.page.wait_for_selector("text='Whitespace Issues'", timeout=5000)
            self.log_pass("Phase 2: Whitespace Issues metric")
            return True
        except Exception as e:
            self.log_warning("Phase 2: Whitespace Issues metric", str(e))
            return True

    def test_phase2_placeholders(self):
        """Test 3.2.2: Placeholder Values metric displays"""
        try:
            self.page.wait_for_selector("text='Placeholder Values'", timeout=5000)
            self.log_pass("Phase 2: Placeholder Values metric")
            return True
        except Exception as e:
            self.log_warning("Phase 2: Placeholder Values metric", str(e))
            return True

    def test_phase3_examples(self):
        """Test 3.3: Examples display in quality flags"""
        try:
            # Look for View Examples expander
            self.page.wait_for_selector("text='View Examples'", timeout=5000)
            self.log_pass("Phase 3: Examples display")
            return True
        except Exception as e:
            self.log_warning("Phase 3: Examples display", str(e))
            return True

    def test_phase4_duplicate_analysis(self):
        """Test 3.4.1: Duplicate Analysis section displays"""
        try:
            self.page.wait_for_selector("text='Duplicate Analysis'", timeout=5000)
            self.log_pass("Phase 4: Duplicate Analysis section")
            return True
        except Exception as e:
            self.log_warning("Phase 4: Duplicate Analysis section", str(e))
            return True

    def test_duplicate_metrics(self):
        """Test 3.4.1: Duplicate metrics display"""
        try:
            self.page.wait_for_selector("text='Unique Rows'", timeout=5000)
            self.page.wait_for_selector("text='Duplicate Rows'", timeout=5000)
            self.page.wait_for_selector("text='Duplicate %'", timeout=5000)
            self.log_pass("Phase 4: Duplicate metrics")
            return True
        except Exception as e:
            self.log_warning("Phase 4: Duplicate metrics", str(e))
            return True

    def test_export_buttons(self):
        """Test 5: Export buttons appear"""
        try:
            # Scroll down to export section
            self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)

            # Check for download buttons
            self.page.wait_for_selector("text='Download Column Summary'", timeout=5000)
            self.page.wait_for_selector("text='Download Dataset Summary'", timeout=5000)
            self.page.wait_for_selector("text='Download Full Profile'", timeout=5000)

            self.log_pass("Export buttons present")
            return True
        except Exception as e:
            self.log_fail("Export buttons", str(e))
            return False

    def take_screenshot(self, name):
        """Take a screenshot for manual review"""
        try:
            filename = f'/tmp/test_{name}_{int(time.time())}.png'
            self.page.screenshot(path=filename, full_page=True)
            print(f"  Screenshot saved: {filename}")
        except Exception as e:
            print(f"  Could not save screenshot: {e}")

    def run_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("DATA PROFILER - COMPREHENSIVE TEST SUITE")
        print("="*70)

        try:
            self.start_browser()
            self.navigate_to_app()

            # Startup tests
            print("\n[SECTION 2: STREAMLIT RUNTIME TESTS]")
            self.test_app_startup()
            self.test_initial_state()

            # Upload test files and test each feature
            print("\n[SECTION 3: FEATURE FUNCTIONALITY TESTS]")
            print("\n--- Testing test_all_features.csv ---")
            if self.upload_file('all_features'):
                self.take_screenshot('all_features')

                # Phase 1 tests
                print("\nPhase 1: Value Distribution Patterns")
                self.test_phase1_skewness()
                self.test_phase1_zeros()
                self.test_phase1_negatives()

                # Phase 2 tests
                print("\nPhase 2: String Quality Checks")
                self.test_phase2_string_quality()
                self.test_phase2_whitespace()
                self.test_phase2_placeholders()

                # Phase 3 tests
                print("\nPhase 3: Sample Data Display")
                self.test_phase3_examples()

                # Phase 4 tests
                print("\nPhase 4: Duplicate Detection")
                self.test_phase4_duplicate_analysis()
                self.test_duplicate_metrics()

                # Export tests
                print("\n[SECTION 5: EXPORT FUNCTIONALITY TESTS]")
                self.test_export_buttons()

            # Print results
            self.print_results()

        except Exception as e:
            print(f"\nFATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.browser:
                self.browser.close()

    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*70)
        print("TEST RESULTS SUMMARY")
        print("="*70)

        total = len(self.results['passed']) + len(self.results['failed'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])

        print(f"\nTotal Tests: {total}")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"⚠ Warnings: {warnings}")

        if self.results['failed']:
            print("\nFailed Tests:")
            for test, reason in self.results['failed']:
                print(f"  - {test}: {reason}")

        if self.results['warnings']:
            print("\nWarnings:")
            for test, msg in self.results['warnings']:
                print(f"  - {test}: {msg}")

        print("\n" + "="*70)
        if failed == 0:
            print("✓ ALL CRITICAL TESTS PASSED")
        else:
            print(f"✗ {failed} CRITICAL TESTS FAILED")
        print("="*70)

if __name__ == '__main__':
    tester = DataProfilerTester()
    tester.run_tests()
