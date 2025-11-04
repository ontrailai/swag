"""
Step 1 Validation Test
Tests configuration loading and directory structure.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_loader import test_config_loader

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1 VALIDATION TEST: Environment & Config")
    print("=" * 60)
    print()

    success = test_config_loader()

    print()
    print("=" * 60)
    if success:
        print("✅ STEP 1 COMPLETE - Ready to proceed to Step 2")
    else:
        print("❌ STEP 1 FAILED - Please fix errors before continuing")
    print("=" * 60)
