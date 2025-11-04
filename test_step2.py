"""
Step 2 Validation Test
Tests Azure Form Recognizer invoice extraction with a single PDF.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_loader import ConfigLoader
from invoice_extractor import test_invoice_extractor

if __name__ == "__main__":
    print("=" * 80)
    print("STEP 2 VALIDATION TEST: Azure Invoice Extraction")
    print("=" * 80)
    print()

    # Load configuration
    try:
        config = ConfigLoader()
        print("✅ Configuration loaded\n")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Test extraction
    result_df = test_invoice_extractor(config)

    print()
    print("=" * 80)
    if result_df is not None and not result_df.empty:
        print("✅ STEP 2 COMPLETE - Ready to proceed to Step 3")
        print()
        print("Extracted columns:", list(result_df.columns))
        print("Sample row:")
        print(result_df.iloc[0].to_dict())
    else:
        print("❌ STEP 2 FAILED - Please fix errors before continuing")
    print("=" * 80)
