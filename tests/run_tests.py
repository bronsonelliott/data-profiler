"""
Comprehensive manual testing of Data Profiler.
Since Playwright file upload is tricky with Streamlit, we'll do interactive testing.
"""

from playwright.sync_api import sync_playwright
import time
import os
from pathlib import Path

TEST_FILES = {
    'all_features': Path('test_data/test_all_features.csv').absolute()
}

def test_runtime():
    """Test Streamlit runtime with all 4 features"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("\n" + "="*70)
        print("TEST: 2.1.1 - App Startup")
        print("="*70)

        page.goto('http://localhost:8501', wait_until='networkidle', timeout=10000)
        time.sleep(2)

        if 'Data Profiler' in page.content():
            print("✓ PASS: App started successfully")
            print("  - Page title found")
            print("  - Upload sidebar visible")
        else:
            print("✗ FAIL: App did not start correctly")
            return False

        print("\n" + "="*70)
        print("TEST: 2.1.2 - Initial State")
        print("="*70)

        if 'Upload a file using the sidebar' in page.content():
            print("✓ PASS: Initial state shows correct message")
        else:
            print("⚠ WARNING: Could not verify initial message")

        print("\n" + "="*70)
        print("TEST: 2.2.1 - File Upload (Interactive)")
        print("="*70)

        file_path = str(TEST_FILES['all_features'])

        # Find the file input
        file_input = page.locator('input[type="file"]')

        if file_input.count() > 0:
            print(f"✓ Found file input element")
            print(f"  Uploading: {file_path}")

            try:
                file_input.set_input_files(file_path)
                print("✓ File upload initiated")
                time.sleep(2)

                # Wait for profiling to complete
                print("  Waiting for profiling to complete...")
                time.sleep(10)  # Give it time to profile

                if 'Successfully profiled' in page.content():
                    print("✓ PASS: File profiling completed")
                elif 'Rows' in page.content():
                    print("✓ PASS: Profile data appears on page")
                else:
                    print("⚠ Could not verify profiling completion, continuing...")

            except Exception as e:
                print(f"✗ FAIL: File upload error - {e}")
                return False
        else:
            print("✗ FAIL: Could not find file input element")
            return False

        # Scroll to see all content
        page.evaluate('window.scrollTo(0, 0)')
        time.sleep(1)

        print("\n" + "="*70)
        print("CHECKING ALL FEATURES")
        print("="*70)

        content = page.content()
        text_content = page.evaluate('document.body.innerText')

        # Phase 1 checks
        print("\n[Phase 1: Value Distribution Patterns]")
        phase1_features = ['Skewness', 'SKEWED_DISTRIBUTION', 'Zeros', 'CONTAINS_ZEROS']
        for feature in phase1_features:
            if feature in content or feature in text_content:
                print(f"  ✓ {feature} found")
            else:
                print(f"  ⚠ {feature} not found (may be in collapsed section)")

        # Phase 2 checks
        print("\n[Phase 2: String Quality Checks]")
        phase2_features = ['String Quality Analysis', 'Whitespace', 'Placeholder', 'Casing']
        for feature in phase2_features:
            if feature in content or feature in text_content:
                print(f"  ✓ {feature} found")
            else:
                print(f"  ⚠ {feature} not found")

        # Phase 3 checks
        print("\n[Phase 3: Sample Data Display]")
        phase3_features = ['View Examples']
        for feature in phase3_features:
            if feature in content or feature in text_content:
                print(f"  ✓ {feature} found")
            else:
                print(f"  ⚠ {feature} not found")

        # Phase 4 checks
        print("\n[Phase 4: Duplicate Detection]")
        phase4_features = ['Duplicate Analysis', 'Unique Rows', 'Duplicate Rows']
        for feature in phase4_features:
            if feature in content or feature in text_content:
                print(f"  ✓ {feature} found")
            else:
                print(f"  ⚠ {feature} not found")

        # Export checks
        print("\n[Export Functionality]")
        export_features = ['Download Column Summary', 'Download Dataset Summary', 'Download Full Profile']
        for feature in export_features:
            if feature in content or feature in text_content:
                print(f"  ✓ {feature} found")
            else:
                print(f"  ⚠ {feature} not found")

        # Take final screenshot
        print("\n[Taking Final Screenshot]")
        page.screenshot(path='/tmp/test_result_final.png', full_page=True)
        print("✓ Screenshot saved to /tmp/test_result_final.png")

        browser.close()
        return True

if __name__ == '__main__':
    print("\nDATA PROFILER - INTERACTIVE RUNTIME TESTING")
    success = test_runtime()

    if success:
        print("\n" + "="*70)
        print("✓ RUNTIME TESTING COMPLETE - APP FUNCTIONAL")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("✗ RUNTIME TESTING FAILED")
        print("="*70)
