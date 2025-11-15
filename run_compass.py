import time
from core import driver_manager
from pages.login_page import LoginPage
from pages.mva_input_page import MVAInputPage
from config.config_loader import get_config
from utils.logger import log
from utils.data_loader import load_mvas
from utils.ui_helpers import is_mva_known, navigate_back_to_home
from flows.work_item_flow import handle_pm_workitems

def main():
    log.info("Starting Compass automation...")

    driver = driver_manager.get_or_create_driver()
    log.debug(f"Driver obtained: {driver}")

    # Login
    login_page = LoginPage(driver)
    log.info("Login page loaded.")
    res = login_page.ensure_ready(
        get_config("username"),
        get_config("password"),
        get_config("login_id"),
    )
    log.info("Login page ready.")

    if res.get("status") != "ok":
        log.error(f"Login failed: {res}")
        return

    time.sleep(1)  # Allow page to settle

    # Load MVAs from CSV
    try:
        mvas = load_mvas("data/mva.csv")
        log.info(f"Loaded {len(mvas)} MVAs from data/mva.csv")
    except FileNotFoundError:
        log.error("data/mva.csv not found. Please create the file with MVA numbers.")
        return
    except Exception as e:
        log.error(f"Error loading MVAs: {e}")
        return

    if not mvas:
        log.warning("No MVAs found in data/mva.csv")
        return

    # Process each MVA
    for mva in mvas:
        log.info("=" * 80)
        log.info(f">>> Starting MVA {mva}")
        log.info("=" * 80)

        # Enter the MVA
        mva_page = MVAInputPage(driver)
        field = mva_page.find_input()
        if not field:
            log.error(f"[MVA] {mva} — input field not found")
            continue

        field.clear()
        field.send_keys(mva)
        time.sleep(3)  # Reduced from 5s

        # Check if MVA is valid
        if not is_mva_known(driver, mva):
            log.warning(f"[MVA] {mva} — invalid/unknown MVA, skipping")
            continue

        # Handle PM Work Items
        res = handle_pm_workitems(driver, mva)

        if res.get("status") in ("ok", "closed"):
            log.info(f"[WORKITEM] {mva} — flow completed successfully")
        elif res.get("status") == "skipped_no_complaint":
            log.info(f"[WORKITEM] {mva} — navigating back home after skip")
            navigate_back_to_home(driver)
            time.sleep(2)  # Reduced from 5s
        else:
            log.warning(f"[WORKITEM] {mva} — failed flow: {res}")

    log.info("Automation run complete.")

if __name__ == "__main__":
    main()
