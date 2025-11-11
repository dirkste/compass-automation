# E2E Validation Requirements

## 🚨 Critical E2E Test Expectations

### What E2E Tests MUST Validate

1. **Pre-Test Data Validation**
   - `data/mva.csv` exists and contains valid MVA numbers
   - Test data is not empty or just comments
   - MVA format validation (numeric strings, appropriate length)

2. **Processing Validation** 
   - Each MVA from test data appears in automation logs
   - Required log pattern: `>>> Starting MVA {mva_number}`
   - All MVAs must be processed (no silent skips)

3. **Post-Test Log Comparison**
   - Compare `data/mva.csv` MVAs against `automation.log` entries
   - Validate 100% processing rate for E2E tests
   - Fail test if any expected MVA is missing from logs

## E2E Test Scripts

### 1. Login-Only Script (`run_compass.py`)
**Purpose**: Basic connectivity and authentication test
**Validates**: 
- ✅ Browser launch and navigation
- ✅ Authentication flow
- ✅ Compass Mobile access
- ❌ Does NOT process MVAs
- ❌ Does NOT validate business logic

### 2. Full E2E Test (`test_mva_complaints_tab_fixed.py`)
**Purpose**: Complete business workflow validation
**Validates**:
- ✅ Full login and MVA processing workflow
- ✅ Data validation using `TestDataValidator`
- ✅ Log comparison for processed MVAs
- ✅ Business logic execution

## Required Log Patterns

### Expected in automation.log:
```
[INFO] [mc.automation] [timestamp] >>> Starting MVA 51299161
[INFO] [mc.automation] [timestamp] >>> Starting MVA 54252855  
[INFO] [mc.automation] [timestamp] >>> Starting MVA 56035512
```

### Test Data Format (data/mva.csv):
```csv
# Test MVAs for E2E validation
51299161
54252855
56035512
```

## Validation Implementation

### Using TestDataValidator:
```python
from utils.test_validation import TestDataValidator

# Pre-test validation
mvas = TestDataValidator.validate_or_skip_e2e_test()
log.info(f"[E2E] Validated test data: {len(mvas)} MVAs to process")

# During processing - REQUIRED log format:
for mva in mvas:
    log.info("=" * 80)
    log.info(f">>> Starting MVA {mva}")  # CRITICAL: This exact format
    log.info("=" * 80)
    # ... process MVA ...

# Post-test validation  
validation_result = TestDataValidator.validate_e2e_execution(require_all_mvas=True)
log.info(f"[E2E] ✅ SUCCESS: {validation_result['processed_count']}/{validation_result['expected_count']} MVAs processed")
```

## Common E2E Validation Failures

### ❌ False Positives (Test passes but shouldn't)
- Test data file empty or missing
- No MVAs actually processed
- Log patterns not matching
- Silent skips due to validation errors

### ❌ False Negatives (Test fails but shouldn't)  
- Log file locked during test execution
- Pattern matching too strict
- Timing issues with log file writes

## Manual Validation

### Run validation report:
```bash
python -c "from utils.test_validation import create_validation_report; print(create_validation_report())"
```

### Expected output:
```
# E2E Test Validation Report

## Summary
- **Expected MVAs**: 3
- **Processed MVAs**: 3
- **Success Rate**: 100.0%

## Validation Status
✅ PASS: All test MVAs were processed
```

## Integration with CI/CD

### Pre-commit validation:
- Ensure `data/mva.csv` has valid test data
- Run E2E validation after any workflow changes
- Fail build if E2E validation fails

### Test execution priority:
1. Run `pytest tests/test_mva_complaints_tab_fixed.py -v` (Full E2E)
2. Validate with `TestDataValidator.validate_e2e_execution()`  
3. Only run `run_compass.py` for connectivity testing

## Files Involved

- **`utils/test_validation.py`**: Core validation logic
- **`tests/test_mva_complaints_tab_fixed.py`**: Full E2E test with validation  
- **`data/mva.csv`**: Test data source
- **`automation.log`**: Execution log for validation
- **`run_compass.py`**: Login-only test (insufficient for E2E)
- **`validate_e2e.py`**: Manual validation script

## Critical Success Factors

1. **Exact Log Format**: Use `>>> Starting MVA {mva}` pattern
2. **Complete Processing**: All test MVAs must appear in logs  
3. **Validation Integration**: Use `TestDataValidator` in all E2E tests
4. **Data Quality**: Maintain valid test MVAs in `data/mva.csv`
5. **Proper Test Selection**: Use full E2E test, not just login test