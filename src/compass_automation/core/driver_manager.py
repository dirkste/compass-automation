import subprocess
import re
import os
import winreg
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.edge.service import Service

from compass_automation.core.driver_downloader import DriverDownloader
from compass_automation.utils.logger import TwoVectorLogger, Verbosity, log

DRIVER_PATH = str(DriverDownloader.DRIVER_PATH)
driver_log = TwoVectorLogger(log, source="DRIVER")

_driver = None  # singleton instance






def get_browser_version() -> str:
    """Return installed Edge browser version from Windows registry."""
    key_candidates = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Edge\BLBeacon"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Edge\BLBeacon"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Edge\BLBeacon"),
    ]

    last_error: Exception | None = None
    for root, subkey in key_candidates:
        try:
            key = winreg.OpenKey(root, subkey)
            value, _ = winreg.QueryValueEx(key, "version")
            if isinstance(value, str) and value.strip():
                return value.strip()
        except Exception as e:
            last_error = e
            continue

    driver_log.error_v(Verbosity.MED, "Failed to read Edge browser version: %s", last_error)
    return "unknown"










def get_driver_version(driver_path: str) -> str:
    """Return Edge WebDriver version (e.g., 140.0.x.x)."""
    if not os.path.exists(driver_path):
        driver_log.warning_v(
            Verbosity.MIN,
            "Driver binary not found at %s (will use Selenium Manager if needed)",
            driver_path,
        )
        return "unknown"
    try:
        output = subprocess.check_output([driver_path, "--version"], text=True)
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output or "")
        if not match:
            driver_log.error_v(
                Verbosity.MED,
                "Failed to get driver version from %s: unrecognized output '%s'",
                driver_path,
                (output or "").strip(),
            )
            return "unknown"
        return match.group(1)
    except Exception as e:
        driver_log.error_v(Verbosity.MED, "Failed to get driver version from %s: %s", driver_path, e)
        return "unknown"


def get_or_create_driver():
    """Return singleton Edge WebDriver, creating it if needed."""
    global _driver
    if _driver:
        return _driver

    browser_ver = get_browser_version()
    driver_ver = get_driver_version(DRIVER_PATH)

    # Always log detected versions
    driver_log.info_v(Verbosity.MIN, "Detected Browser=%s, Driver=%s", browser_ver, driver_ver)

    # Compare before launching browser (only when we have an actual local driver version).
    if driver_ver == "unknown":
        driver_log.info_v(
            Verbosity.MIN,
            "Driver version unknown (no local msedgedriver.exe); Selenium Manager may be used",
        )
    else:
        if browser_ver.split(".")[0] != driver_ver.split(".")[0]:
            driver_log.warning_v(
                Verbosity.MED,
                "Version mismatch → Browser %s, Driver %s. Proceeding with caution. Run 'python manage_driver.py --download' to update.",
                browser_ver,
                driver_ver,
            )
        else:
            driver_log.info_v(Verbosity.MIN, "Versions match")

    try:
        driver_log.info_v(Verbosity.MIN, "Launching Edge → Browser %s, Driver %s", browser_ver, driver_ver)
        options = webdriver.EdgeOptions()
        options.add_argument("--inprivate")
        options.add_argument("--start-maximized")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 2 }) 
        
        if os.path.exists(DRIVER_PATH):
            service = Service(DRIVER_PATH)
            _driver = webdriver.Edge(service=service, options=options)
        else:
            driver_log.warning_v(Verbosity.MED, "Driver not found at %s; falling back to Selenium Manager", DRIVER_PATH)
            _driver = webdriver.Edge(options=options)
            
        return _driver
    except SessionNotCreatedException as e:
        driver_log.error_v(Verbosity.MIN, "Session creation failed: %s", e)
        raise


def quit_driver():
    """Quit and reset the singleton driver."""
    global _driver
    if _driver:
        driver_log.info_v(Verbosity.MIN, "Quitting Edge WebDriver...")
        try:
            quit_fn = getattr(_driver, "quit", None)
            if callable(quit_fn):
                quit_fn()
            else:
                driver_log.warning_v(Verbosity.MED, "Singleton driver has no quit(): %r", _driver)
        finally:
            _driver = None
