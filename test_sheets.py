"""
Google Sheets Integration Test
Tests Google Sheets authentication and writing capabilities.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_loader import ConfigLoader
from sheets_writer import test_sheets_writer

if __name__ == "__main__":
    print("=" * 80)
    print("GOOGLE SHEETS INTEGRATION TEST")
    print("=" * 80)
    print()
    print("This test will:")
    print("1. Verify Google Sheets configuration")
    print("2. Authenticate with Google Sheets API (may open browser)")
    print("3. Write a test row to your Google Sheet")
    print()
    input("Press Enter to continue or Ctrl+C to cancel...")
    print()

    # Load configuration
    try:
        config = ConfigLoader()
        print("✅ Configuration loaded\n")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Test Google Sheets writer
    success = test_sheets_writer(config)

    print()
    print("=" * 80)
    if success:
        print("✅ GOOGLE SHEETS INTEGRATION COMPLETE")
        print()
        print("Next steps:")
        print("1. Check your Google Sheet to verify the test row was added")
        print("2. Ready to proceed with full integration")
    else:
        print("❌ GOOGLE SHEETS INTEGRATION FAILED")
        print()
        print("Common issues:")
        print("- Missing credentials.json file")
        print("- Invalid Google Sheet ID in config.json")
        print("- Sheet tab name doesn't match config")
        print("- Insufficient permissions on the Google Sheet")
    print("=" * 80)
