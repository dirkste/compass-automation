import time

import pytest
from selenium.webdriver.common.by import By
from config.config_loader import get_config
from core import driver_manager
from pages.login_page import LoginPage
from pages.mva_input_page import MVAInputPage
from utils.data_loader import load_mvas
from utils.logger import log
from utils.project_paths import ProjectPaths
from utils.ui_helpers import navigate_back_to_home, is_mva_known
from utils.test_validation import TestDataValidator

# Load config values
USERNAME = get_config("username")
PASSWORD = get_config("password")
LOGIN_ID = get_config("login_id")
DELAY = get_config("delay_seconds", default=2)


@pytest.mark.smoke
def test_mva_complaints_tab():
    print("Starting test_mva_complaints_tab...")
    
    # Add clear test session header
    import uuid
    from datetime import datetime
    session_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log.info("=" * 80)
    log.info("🚀 E2E TEST SESSION STARTED")
    log.info(f"📋 Session ID: {session_id}")
    log.info(f"📅 Timestamp: {timestamp}")
    log.info(f"🧪 Test: test_mva_complaints_tab")
    log.info("=" * 80)

    # Initialize driver
    driver = driver_manager.get_or_create_driver()
    log.info(f"Driver initialized: {driver}")

    # Perform login
    login_page = LoginPage(driver)
    res = login_page.ensure_ready(USERNAME, PASSWORD, LOGIN_ID)
    if res["status"] != "ok":
        pytest.skip(f"Login failed -> {res}")
    time.sleep(DELAY)  # configurable settle

    # Load and validate test data - CRITICAL: This ensures E2E actually runs
    mvas = TestDataValidator.validate_or_skip_e2e_test()
    log.info(f"[E2E] Validated test data: {len(mvas)} MVAs to process")
    
    # Store expected MVAs for post-test validation
    expected_mvas = set(mvas)

    # Loop through MVAs
    for mva in mvas:
        log.info("=" * 80)
        log.info(f">>> Starting MVA {mva}")
        log.info("=" * 80)

        # Enter the MVA into the input field
        mva_page = MVAInputPage(driver)
        field = mva_page.find_input()
        if not field:
            res = {"status": "failed", "reason": "mva_input_not_found"}
            log.error(f"[MVA] {mva} — input field not found")
            assert res["status"] == "ok", f"Flow failed: {res}"

        field.clear()
        field.send_keys(mva)
        # Check if MVA is valid before proceeding with work items

        time.sleep(5)

        from utils.ui_helpers import is_mva_known, get_lighthouse_status
        if not is_mva_known(driver, mva):
            log.warning(f"[MVA] {mva} — invalid/unknown MVA, skipping")
            continue

        # Check Lighthouse status for early exit
        # lighthouse_status = get_ lighthouse_status(driver, mva)
        # if lighthouse_status == "Rentable":
        #     log.info(f"[MVA] {mva} — Lighthouse status is 'Rentable', skipping further processing.")
        #     continue

        # Handle PM Work Items in one call
        from flows.work_item_flow import handle_pm_workitems
        res = handle_pm_workitems(driver, mva)

        if res.get("status") in ("ok", "closed"):
            log.info(f"[WORKITEM] {mva} — flow completed successfully")
        elif res.get("status") == "skipped_no_complaint":
            log.info(f"[WORKITEM] {mva} — navigating back home after skip")
            navigate_back_to_home(driver)
            time.sleep(5)
        else:
            log.warning(f"[WORKITEM] {mva} — failed flow: {res}")
    
    # CRITICAL POST-TEST VALIDATION: Ensure all test MVAs were actually processed
    log.info("[E2E] Starting post-test validation to verify MVA processing...")
    try:
        validation_result = TestDataValidator.validate_e2e_execution(require_all_mvas=True)
        log.info(f"[E2E] ✅ VALIDATION SUCCESS: {validation_result['processed_count']}/{validation_result['expected_count']} MVAs processed")
    except Exception as e:
        log.error(f"[E2E] ❌ VALIDATION FAILED: {str(e)}")
        pytest.fail(f"E2E Validation Failed: {str(e)}")
    
    log.info("[E2E] Test completed - all MVAs processed and validated")