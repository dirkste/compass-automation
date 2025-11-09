#!/usr/bin/env python3
"""
Manual E2E validation script.

Run this script after E2E tests to verify that all test MVAs 
were actually processed in the automation logs.

Usage:
    python validate_e2e.py
    python validate_e2e.py --require-all
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.test_validation import TestDataValidator, create_validation_report, E2EValidationError


def main():
    parser = argparse.ArgumentParser(description="Validate E2E test execution")
    parser.add_argument(
        "--require-all", 
        action="store_true",
        help="Require all test MVAs to be processed (fail if any missing)"
    )
    parser.add_argument(
        "--log-file",
        default="automation.log",
        help="Log file to analyze (default: automation.log)"
    )
    
    args = parser.parse_args()
    
    print("🔍 E2E Test Validation")
    print("=" * 50)
    
    try:
        # Generate validation report
        report = create_validation_report()
        print(report)
        
        # Perform strict validation if requested
        if args.require_all:
            print("\n🚨 Performing STRICT validation (require all MVAs)...")
            try:
                result = TestDataValidator.validate_e2e_execution(require_all_mvas=True)
                print(f"✅ STRICT VALIDATION PASSED: {result['processed_count']}/{result['expected_count']} MVAs processed")
                return 0
            except E2EValidationError as e:
                print(f"❌ STRICT VALIDATION FAILED:")
                print(f"   {str(e)}")
                return 1
        else:
            print("\n✅ Report generated successfully")
            print("💡 Use --require-all for strict validation")
            return 0
            
    except Exception as e:
        print(f"❌ Validation Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())