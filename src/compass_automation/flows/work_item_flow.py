"""Flows for creating, processing, and handling Compass Work Items."""
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from compass_automation.flows.complaints_flows import associate_existing_complaint
from compass_automation.flows.finalize_flow import finalize_workitem
from compass_automation.utils.logger import TwoVectorLogger, Verbosity, log
from compass_automation.utils.ui_helpers import click_element, safe_wait


work_log = TwoVectorLogger(log, source="WORKITEM")
workitems_log = TwoVectorLogger(log, source="WORKITEMS")
complaint_log = TwoVectorLogger(log, source="COMPLAINT")
dialog_log = TwoVectorLogger(log, source="DIALOG")

def get_work_items(driver, mva: str):
    """Collect all open PM work items for the given MVA."""
    work_log.info_v(Verbosity.MED, "%s - pausing to let Work Items render...", mva)
    time.sleep(9)  # wait for UI to render
    try:
        tiles = driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'scan-record-header') "
            "and .//div[contains(@class,'scan-record-header-title')][contains(normalize-space(),'PM')] "
            "and .//div[contains(@class,'scan-record-header-title-right__')][normalize-space()='Open']]"
        )
        workitems_log.info_v(Verbosity.MIN, "%s - collected %s open PM item(s)", mva, len(tiles))
        for t in tiles:
            workitems_log.info_v(Verbosity.FULL, "%s - tile text=%r", mva, t.text)
        return tiles
    except NoSuchElementException as e:
        work_log.warning_v(Verbosity.MED, "%s - could not collect work items -> %s", mva, e)
        return []





def create_new_workitem(driver, mva: str):
    """Create a new Work Item for the given MVA."""
    work_log.info_v(Verbosity.MIN, "%s - starting CREATE NEW WORK ITEM workflow", mva)

    # Step 1: Click Add Work Item
    try:
        time.sleep(5)  # wait for button to appear
        if not click_element(driver, (By.XPATH, "//button[normalize-space()='Add Work Item']")):
            work_log.warning_v(Verbosity.MED, "%s - add_btn not found", mva)
            return {"status": "failed", "reason": "add_btn", "mva": mva}
        work_log.info_v(Verbosity.MIN, "%s - Add Work Item clicked", mva)
        time.sleep(5)

    except NoSuchElementException as e:
        work_log.warning_v(Verbosity.MED, "%s - add_btn failed -> %s", mva, e)
        return {"status": "failed", "reason": "add_btn", "mva": mva}

    # Step 2: Complaint handling
    try:
        res = associate_existing_complaint(driver, mva)
        if res["status"] == "associated":
            complaint_log.info_v(
                Verbosity.MIN,
                "%s - existing PM complaint linked to Work Item",
                mva,
            )
        else:
            work_log.info_v(Verbosity.MIN, "%s - no existing PM complaint, navigating back", mva)
            return {"status": "skipped_no_complaint", "mva": mva}
    except NoSuchElementException as e:
        work_log.warning_v(Verbosity.MED, "%s - complaint handling failed -> %s", mva, e)
        return {"status": "failed", "reason": "complaint_handling", "mva": mva}

    # Step 3: Finalize Work Item (call will be injected here in refactor later)
    work_log.warning_v(Verbosity.MED, "%s - finalize step skipped (refactor placeholder)", mva)
    return {"status": "created", "mva": mva}


def handle_pm_workitems(driver, mva: str) -> dict:
    """
    Handle PM Work Items for a given MVA:
      1. If an open PM Work Item exists, complete it.
      2. Otherwise, start a new Work Item.
         - Try to associate an existing complaint.
         - If none, skip and return control to the test loop.
    """
    work_log.info_v(Verbosity.MIN, "%s — handling PM work items", mva)

    # Step 1: check for open PM Work Items
    items = get_work_items(driver, mva)
    if items:
        work_log.info_v(Verbosity.MIN, "%s - open PM Work Item found, completing it", mva)
        from compass_automation.flows.work_item_flow import complete_pm_workitem
        return complete_pm_workitem(driver, mva)

    # Step 2: no open WI → start a new one
    from selenium.webdriver.common.by import By
    if click_element(driver, (By.XPATH, "//button[normalize-space()='Add Work Item']"),
                     desc="Add Work Item", timeout=8):
        work_log.info_v(Verbosity.MIN, "%s - Add Work Item clicked", mva)

        # Required Action: immediately try to associate existing complaints
        from compass_automation.flows.complaints_flows import associate_existing_complaint
        res = associate_existing_complaint(driver, mva)

        if res.get("status") == "associated":
            from compass_automation.flows.finalize_flow import finalize_workitem
            return finalize_workitem(driver, mva)

        elif res.get("status") == "skipped_no_complaint":
            work_log.info_v(Verbosity.MIN, "%s — navigating back home after skip", mva)
            from compass_automation.utils.ui_helpers import navigate_back_to_home
            navigate_back_to_home(driver)
            return res

        return res

    else:
        work_log.warning_v(Verbosity.MED, "%s - could not click Add Work Item", mva)
        return {"status": "failed", "reason": "add_btn", "mva": mva}







def process_workitem(driver, mva: str):
    """Main entry point for processing a Work Item for the given MVA."""
    work_log.info_v(Verbosity.MIN, "%s - starting process", mva)

    # Step 1: Gather existing Work Items
    tiles = get_work_items(driver, mva)
    total = len(tiles)
    work_log.info_v(Verbosity.MIN, "%s - %s total work items found", mva, total)

    if total == 0:
        work_log.info_v(Verbosity.MIN, "%s - no PM work items found", mva)
        return {"status": "skipped", "reason": "no_pm_workitems", "mva": mva}

    # Step 2: Handle existing Open PM Work Items
    res = complete_pm_workitem(driver, mva, timeout=8)
    return res



def open_pm_workitem_card(driver, mva: str, timeout: int = 8) -> dict:
    """Find and open the first Open PM Work Item card."""
    try:
        tile = driver.find_element(
            By.XPATH,
            (
                "//div[contains(@class,'scan-record-header') "
                "and .//div[contains(@class,'scan-record-header-title')]"
                "[normalize-space()='PM' or normalize-space()='PM Hard Hold - PM'] "
                "and .//div[contains(@class,'scan-record-header-title-right')][normalize-space()='Open']]"
            )
        )
        tile.click()
        work_log.info_v(Verbosity.MIN, "%s - Open PM Work Item card clicked", mva)
        return {"status": "ok", "reason": "card_opened", "mva": mva}
    except Exception as e:
        work_log.warning_v(Verbosity.MED, "%s - could not open Open PM Work Item card -> %s", mva, e)
        return {"status": "failed", "reason": "open_pm_card", "mva": mva}

def complete_work_item_dialog(driver, note: str = "Done", timeout: int = 10, observe: int = 0) -> dict:
    """Fill the correction dialog with note and click 'Complete Work Item'."""
    try:
        # 1) Wait for visible dialog root
        dialog = safe_wait(
            driver,
            timeout,
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bp6-dialog")),
            desc="Work Item dialog"
        )

        dialog_log.info_v(Verbosity.MIN, "Correction dialog opened")

        # 2) Find textarea (scoped to dialog)
        textarea = safe_wait(
            driver,
            timeout,
            EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea.bp6-text-area")),
            desc="Correction textarea"
        )
        #TODO: Clean up sleeps later
        textarea.click()
        textarea.clear()
        time.sleep(5)
        textarea.send_keys(note)
        time.sleep(5)
        dialog_log.info_v(Verbosity.MED, "Entered note text: %r", note)
        time.sleep(5)

        # 3) Click 'Complete Work Item'
        complete_btn = safe_wait(
            driver,
            timeout,
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'bp6-dialog')]//button[normalize-space()='Complete Work Item']")),
            desc="Complete Work Item button"
        )
        time.sleep(5)

        complete_btn.click()
        dialog_log.info_v(Verbosity.MIN, "'Complete Work Item' button clicked")
    

        # 4) Wait for dialog to close
        safe_wait(driver ,timeout, EC.invisibility_of_element(dialog), desc="Dialog to close")    

        dialog_log.info_v(Verbosity.MIN, "Correction dialog closed")

        # The issue might be that closing the UI short after clicking the button 
        # doesn't give enough time for the backend to process the completion.
        # Adding a longer wait here to ensure the process completes before proceeding.
        time.sleep(30)

        return {"status": "ok"}
    except Exception as e:
        dialog_log.error_v(Verbosity.MIN, "complete_work_item_dialog -> %s", e)
        return {"status": "failed", "reason": "dialog_exception"}



def mark_complete_pm_workitem(driver, mva: str, note: str = "Done", timeout: int = 8) -> dict:
    """Click 'Mark Complete', then complete the dialog with the given note."""
    if not click_element(driver, (By.CSS_SELECTOR, "button.fleet-operations-pwa__mark-complete-button__spuz8c")):
        if not click_element(driver, (By.XPATH, "//button[normalize-space()='Mark Complete']")):
            return {"status": "failed", "reason": "mark_complete_button", "mva": mva}

    time.sleep(0.2)
    res = complete_work_item_dialog(driver, note=note, timeout=max(10, timeout), observe=1)
    TwoVectorLogger(log, source="MARKCOMPLETE").info_v(Verbosity.MED, "complete_work_item_dialog -> %r", res)

    if res and res.get("status") == "ok":
        return {"status": "ok", "reason": "dialog_complete", "mva": mva}
    else:
        return {"status": "failed", "reason": res.get("reason", "dialog_failed"), "mva": mva}




def complete_pm_workitem(driver, mva: str, timeout: int = 8) -> dict:
    """Open the PM Work Item card and mark it complete with note='Done'."""
    time.sleep(9)  # wait for UI to stabilize
    res = open_pm_workitem_card(driver, mva, timeout=timeout)
    if res.get("status") != "ok":
        return res  # pass through failure dict
    time.sleep(9)  # wait for card to open
    res = mark_complete_pm_workitem(driver, mva, note="Done", timeout=timeout)
    time.sleep(9)  # wait for completion to process
    if res.get("status") == "ok":
        return {"status": "ok", "reason": "completed_open_pm", "mva": mva}
    else:
        return {"status": "failed", "reason": res.get("reason", "mark_complete"), "mva": mva}