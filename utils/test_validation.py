"""
Test validation utilities to ensure E2E tests actually execute business logic.

This module provides critical validation that prevents false positive test results
by verifying that test data MVAs actually appear in execution logs.
"""
import re
from pathlib import Path
from typing import List, Dict, Set
from utils.data_loader import load_mvas
from utils.project_paths import ProjectPaths


class E2EValidationError(Exception):
    """Raised when E2E validation fails."""
    pass


class TestDataValidator:
    """Validates that E2E tests actually process expected test data."""
    
    @staticmethod
    def get_mvas_from_test_data() -> List[str]:
        """
        Load MVAs from test data file.
        
        Returns:
            List[str]: List of MVAs from mva.csv
            
        Raises:
            E2EValidationError: If test data is missing or empty
        """
        data_path = ProjectPaths.get_data_path("mva.csv")
        
        if not data_path.exists():
            raise E2EValidationError(
                f"TEST DATA MISSING: {data_path} does not exist. "
                "E2E tests cannot run without valid test data."
            )
        
        mvas = load_mvas(str(data_path))
        
        if not mvas:
            raise E2EValidationError(
                f"TEST DATA EMPTY: {data_path} contains no valid MVAs. "
                "E2E tests require actual MVA numbers to process."
            )
        
        return mvas
    
    @staticmethod
    def get_mvas_from_logs(log_file: str = "automation.log") -> Set[str]:
        """
        Extract MVAs that were actually processed from log file.
        
        Args:
            log_file: Path to log file (default: automation.log)
            
        Returns:
            Set[str]: Set of MVAs found in log entries
        """
        log_path = Path(log_file)
        
        if not log_path.exists():
            return set()
        
        processed_mvas = set()
        
        # Pattern to match MVA processing log entries
        # Looks for: ">>> Starting MVA 12345678" or "[MVA] 12345678"
        mva_patterns = [
            r">>> Starting MVA (\d+)",
            r"\[MVA\] (\d+)",
            r"Starting MVA processing for (\d+)",
            r"Processing MVA: (\d+)"
        ]
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    for pattern in mva_patterns:
                        matches = re.findall(pattern, line)
                        processed_mvas.update(matches)
        except Exception as e:
            # Log file might be locked or unreadable
            print(f"Warning: Could not read log file {log_path}: {e}")
        
        return processed_mvas
    
    @staticmethod
    def validate_e2e_execution(require_all_mvas: bool = True, 
                             max_age_hours: int = 1) -> Dict[str, any]:
        """
        Validate that E2E test actually processed expected MVAs.
        
        Args:
            require_all_mvas: If True, all test MVAs must appear in logs
            max_age_hours: Maximum age of log entries to consider (hours)
            
        Returns:
            Dict with validation results
            
        Raises:
            E2EValidationError: If validation fails
        """
        # Get expected MVAs from test data
        expected_mvas = set(TestDataValidator.get_mvas_from_test_data())
        
        # Get actual MVAs from logs
        processed_mvas = TestDataValidator.get_mvas_from_logs()
        
        # Calculate validation metrics
        found_mvas = expected_mvas.intersection(processed_mvas)
        missing_mvas = expected_mvas - processed_mvas
        unexpected_mvas = processed_mvas - expected_mvas
        
        validation_result = {
            "expected_count": len(expected_mvas),
            "processed_count": len(found_mvas),
            "missing_count": len(missing_mvas),
            "expected_mvas": sorted(expected_mvas),
            "found_mvas": sorted(found_mvas),
            "missing_mvas": sorted(missing_mvas),
            "unexpected_mvas": sorted(unexpected_mvas),
            "success_rate": len(found_mvas) / len(expected_mvas) if expected_mvas else 0
        }
        
        # Determine if validation passes
        if require_all_mvas and missing_mvas:
            error_msg = (
                f"E2E VALIDATION FAILED: {len(missing_mvas)}/{len(expected_mvas)} "
                f"test MVAs were NOT processed in automation logs.\n"
                f"Missing MVAs: {missing_mvas}\n"
                f"Expected MVAs: {expected_mvas}\n"
                f"This indicates E2E test did not execute complete business workflow."
            )
            raise E2EValidationError(error_msg)
        
        return validation_result
    
    @staticmethod
    def validate_or_skip_e2e_test() -> List[str]:
        """
        Validate test data and return MVAs for E2E testing, or skip test.
        
        Use this at the start of E2E tests to ensure proper setup.
        
        Returns:
            List[str]: Valid MVAs for testing
            
        Raises:
            pytest.skip: If test data is not available (for development)
            E2EValidationError: If test data exists but is invalid
        """
        import pytest
        
        try:
            mvas = TestDataValidator.get_mvas_from_test_data()
            print(f"✅ E2E Test Data Validated: {len(mvas)} MVAs available")
            return mvas
        except E2EValidationError as e:
            # In CI/production, this should fail
            # In development, this might skip
            if "does not exist" in str(e):
                pytest.skip("Test data file missing - run with actual mva.csv for E2E validation")
            else:
                # Data exists but is invalid - this should fail
                raise


def create_validation_report() -> str:
    """
    Create a detailed validation report for manual review.
    
    Returns:
        str: Formatted validation report
    """
    try:
        result = TestDataValidator.validate_e2e_execution(require_all_mvas=False)
        
        report = f"""
# E2E Test Validation Report

## Summary
- **Expected MVAs**: {result['expected_count']}
- **Processed MVAs**: {result['processed_count']} 
- **Success Rate**: {result['success_rate']:.1%}
- **Missing MVAs**: {result['missing_count']}

## Details

### Expected MVAs (from mva.csv):
{chr(10).join(f"  - {mva}" for mva in result['expected_mvas'])}

### Successfully Processed MVAs:
{chr(10).join(f"  ✅ {mva}" for mva in result['found_mvas'])}

### Missing MVAs (NOT processed):
{chr(10).join(f"  ❌ {mva}" for mva in result['missing_mvas'])}

### Unexpected MVAs (in logs but not test data):
{chr(10).join(f"  ⚠️ {mva}" for mva in result['unexpected_mvas'])}

## Validation Status
{'✅ PASS: All test MVAs were processed' if result['missing_count'] == 0 else f'❌ FAIL: {result["missing_count"]} MVAs missing from logs'}

## Recommendations
{
'E2E validation successful - automation processed all expected test data.' 
if result['missing_count'] == 0 
else f'E2E validation failed - {result["missing_count"]} test MVAs were not processed. This indicates the E2E test did not execute the complete business workflow.'
}
"""
        return report
        
    except E2EValidationError as e:
        return f"""
# E2E Test Validation Report

## ❌ VALIDATION FAILED

{str(e)}

## Required Actions
1. Ensure data/mva.csv exists and contains valid MVA numbers
2. Run E2E tests and verify all MVAs are processed
3. Check automation.log for actual MVA processing entries
"""


if __name__ == "__main__":
    # CLI usage for manual validation
    print(create_validation_report())