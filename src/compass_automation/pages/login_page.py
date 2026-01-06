import json
import time
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC


from compass_automation.core.navigator import Navigator
from compass_automation.utils.project_paths import ProjectPaths
from compass_automation.utils.logger import TwoVectorLogger, log
from compass_automation.utils.ui_helpers import click_and_expect, safe_wait, send_text, wait_for_any


login_log = TwoVectorLogger(log, source="LOGIN")


_LOGIN_BLOCKERS = [
    {
        "reason": "unexpected_account_picker",
        "locator": (
            By.XPATH,
            "//*[contains(normalize-space(),'Pick an account') or contains(normalize-space(),'Use another account')]",
        ),
        "mode": "visible",
    },
    {
        "reason": "unexpected_mfa_required",
        "locator": (
            By.XPATH,
            "//*[contains(normalize-space(),'Approve sign in request') or contains(normalize-space(),'Enter code') or contains(normalize-space(),'verification')]",
        ),
        "mode": "visible",
    },
    {
        "reason": "unexpected_mfa_required",
        "locator": (By.NAME, "otc"),
        "mode": "present",
    },
    {
        "reason": "unexpected_consent_required",
        "locator": (
            By.XPATH,
            "//*[contains(normalize-space(),'Permissions requested') or contains(normalize-space(),'Need admin approval') or contains(normalize-space(),'consent')]",
        ),
        "mode": "visible",
    },
    {
        "reason": "unexpected_conditional_access",
        "locator": (By.XPATH, "//*[contains(normalize-space(),'More information required')]"),
        "mode": "visible",
    },
]


class LoginPage:
    def __init__(self, driver):
        self.driver = driver

        # Use centralized path management
        config_path = ProjectPaths.get_config_path()
        with open(config_path, "r") as f:
            config = json.load(f)
            self.delay_seconds = config.get("delay_seconds", 4)

    def is_logged_in(self):
        """Check if Compass Mobile session is already authenticated."""
        
        login_log.info("inside is_logged_in")
        elems = self.driver.find_elements(By.XPATH, "//span[contains(text(),'Compass Mobile')]")
        return len(elems) > 0

    def ensure_logged_in(self, username: str, password: str, login_id: str):
        # Always navigate first
        Navigator(self.driver).go_to(
            "https://avisbudget.palantirfoundry.com/multipass/login", label="Login page"
        )

        if self.is_logged_in():
            login_log.info("Session already authenticated - reusing it.")
            return {"status": "ok"}
        else:
            login_log.info("No active session - performing login()...")
            return self.login(username, password, login_id)

    def enter_wwid(self, login_id: str):
        """Actually type and submit the WWID once."""
        try:
            safe_wait(
                self.driver,
                10,
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[class*='fleet-operations-pwa__text-input__']")
                ),
                desc="WWID input"
            )

        except TimeoutException:
            login_log.warning("Timed out waiting for WWID field")
            return {"status": "failed", "reason": "wwid_field_timeout"}

        try:
            # Use send_text for the actual entry
            if not send_text(
                self.driver,
                (By.CSS_SELECTOR, "input[class*='fleet-operations-pwa__text-input__']"),
                login_id,
            ):
                return {"status": "failed", "reason": "wwid_entry_failed"}

            submit_res = click_and_expect(
                self.driver,
                (By.XPATH, "//button[.//span[normalize-space()='Submit']]") ,
                click_desc="WWID submit",
                expectations=[
                    {
                        "name": "mva_home",
                        "locator": (By.XPATH, "//button[contains(@class,'fleet-operations-pwa__camera-button')]"),
                        "mode": "present",
                    }
                ],
                blockers=_LOGIN_BLOCKERS,
                timeout_click=10,
                timeout_expect=20,
                label="post_wwid_submit",
            )
            if submit_res.get("status") != "ok":
                login_log.warning(f"WWID submit did not transition: {submit_res}")
                return {"status": "failed", "reason": "wwid_submit_no_transition"}

            login_log.info("WWID submit -> home screen detected")
            return {"status": "ok"}
            # time.sleep(5)


        except Exception as e:
            login_log.error(f"Unexpected error entering WWID: {e}")
            return {"status": "failed", "reason": "exception"}

    def login(self, username: str, password: str, login_id: str):
        """Perform login flow: email -> password -> stay signed in"""
        # Navigation via Navigator (SRP)
        
        login_log.info("inside login()")
        Navigator(self.driver).go_to(
            "https://avisbudget.palantirfoundry.com/multipass/login", label="Login page", verify=False
        )

        # Evidence that the login form exists before we attempt any actions.
        nav_check = Navigator(self.driver).verify(check_locator=(By.NAME, "loginfmt"), timeout=15)
        if nav_check.get("status") != "ok":
            login_log.warning(f"Login page not ready for input: {nav_check}")
            return {"status": "failed", "reason": "login_page_not_ready"}

        # --- Email ---
        if not send_text(
            self.driver,
            (By.NAME, "loginfmt"),
            username,
            timeout=10,
            clear=True,
            validate=True,
            label="email_field",
        ):
            login_log.warning("Failed to enter email (field not clickable or did not accept input)")
            return {"status": "failed", "reason": "email_entry_failed"}


        login_log.info("Email entered")

        # Click Next button to proceed to password
        next_res = click_and_expect(
            self.driver,
            (By.ID, "idSIButton9"),
            click_desc="Next after email",
            expectations=[
                {"name": "password_field", "locator": (By.NAME, "passwd"), "mode": "present"},
            ],
            blockers=_LOGIN_BLOCKERS,
            timeout_expect=15,
            label="post_next_after_email",
        )
        if next_res.get("status") != "ok":
            login_log.warning(f"Next after email did not transition: {next_res}")
            return {"status": "failed", "reason": "login_transition_missing_password_field"}

        login_log.info("Next after email -> password step detected")
        # --- Password ---
        if not send_text(
            self.driver,
            (By.NAME, "passwd"),
            password,
            timeout=10,
            clear=True,
            validate=False,
            label="password_field",
        ):
            login_log.warning("Failed to enter password (field not clickable or did not accept input)")
            return {"status": "failed", "reason": "password_entry_failed"}

        login_log.info("Password entered")

        signin_res = click_and_expect(
            self.driver,
            (By.ID, "idSIButton9"),
            click_desc="Sign in button",
            expectations=[
                # Expected: KMSI prompt OR redirect to app shell.
                {"name": "kmsi_prompt", "locator": (By.ID, "idBtn_Back"), "mode": "clickable"},
                {
                    "name": "app_shell",
                    "locator": (By.XPATH, "//span[contains(text(),'Compass Mobile')]|//a[@role='button']//span[normalize-space()='Compass Mobile']"),
                    "mode": "present",
                },
            ],
            blockers=_LOGIN_BLOCKERS,
            timeout_expect=20,
            label="post_signin",
        )
        if signin_res.get("status") != "ok":
            login_log.warning(f"Sign in did not reach expected state: {signin_res}")
            return {"status": "failed", "reason": "login_post_signin_no_transition"}

        login_log.info(f"Sign in -> matched {signin_res.get('matched')}")

        # --- Stay signed in? ---
        if signin_res.get("matched") == "kmsi_prompt":
            no_btn = safe_wait(
                self.driver,
                6,
                EC.element_to_be_clickable((By.ID, "idBtn_Back")),
                "stay_signed_in_no",
            )
            login_log.info("Dismissing 'Stay signed in?' dialog with No")
            no_btn.click()

            post_kmsi = wait_for_any(
                self.driver,
                expectations=[
                    {
                        "name": "app_shell",
                        "locator": (
                            By.XPATH,
                            "//span[contains(text(),'Compass Mobile')]|//a[@role='button']//span[normalize-space()='Compass Mobile']",
                        ),
                        "mode": "present",
                    }
                ],
                blockers=_LOGIN_BLOCKERS,
                timeout=20,
                label="post_kmsi_no",
            )
            if post_kmsi.get("status") != "ok":
                login_log.warning(f"KMSI dismissed but app shell not detected: {post_kmsi}")
                return {"status": "failed", "reason": "login_post_kmsi_no_transition"}
        else:
            login_log.info("KMSI prompt not shown")

        return {"status": "ok"}

    def go_to_mobile_home(self):
        """Navigate from Foundry to Compass Mobile tab and verify WWID screen appears."""
        mobile_btn = safe_wait(
            self.driver,
            10,
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[@role='button']//span[normalize-space()='Compass Mobile']",
                )
            ),
            "compass_mobile_button",
        )

        if not mobile_btn:
            login_log.warning("Compass Mobile button not found")
            return {"status": "failed", "reason": "compass_mobile_button_missing"}

        # Save current tab count
        prev_tabs = len(self.driver.window_handles)

        login_log.info("Clicking Compass Mobile button")
        mobile_btn.click()

        safe_wait(
            self.driver,
            10,
            lambda d: len(d.window_handles) > prev_tabs,
            desc="New tab to open"
        )


        # Confirm new tab appeared
        curr_tabs = len(self.driver.window_handles)
        if curr_tabs <= prev_tabs:
            login_log.warning("No new tab detected after clicking Compass Mobile")
            return {"status": "failed", "reason": "no_new_tab"}

        # Switch to newest tab
        self.driver.switch_to.window(self.driver.window_handles[-1])
        login_log.info("Switched to Compass Mobile tab")

        # Verify WWID field exists
        wwid_field = safe_wait(
            self.driver,
            10,
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[class*='fleet-operations-pwa__text-input__']")
            ),
            "wwid_input_field",
        )
        if not wwid_field:
            login_log.warning("WWID input not found after Compass Mobile launch")
            return {"status": "failed", "reason": "wwid_field_missing"}

        login_log.info("WWID input field detected")
        return {"status": "ok"}

    def ensure_user_context(self, login_id: str):
        """Ensure WWID is entered once Compass Mobile is loaded."""
        login_log.info("Proceeding to WWID entry")
        return self.enter_wwid(login_id)

    def ensure_ready(self, username: str, password: str, login_id: str):
        """
        High-level pretest setup:
        1) ensure_logged_in
        2) go_to_mobile_home
        3) ensure_user_context(WWID)
        """
        login_log.info("before ensure_logged_in")

        res = self.ensure_logged_in(username, password, login_id)
        login_log.debug(f"ensure_logged_in -> {res}")
        time.sleep(self.delay_seconds)
        if res["status"] != "ok":
            return res

        res = self.go_to_mobile_home()
        if res["status"] != "ok":
            return res

        res = self.ensure_user_context(login_id)
        return res
