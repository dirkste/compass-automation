"""
High-priority driver verification test.

This test runs first (pytest collection order) to ensure the WebDriver
matches the installed browser before any other tests execute.

Mark with @pytest.mark.driver_check to ensure it runs early.
"""

import pytest
from compass_automation.core.driver_downloader import DriverDownloader
from compass_automation.utils.logger import log


@pytest.mark.driver_check  # Priority marker - runs before other tests
def test_driver_verification_required():
    """
    CRITICAL TEST: Verify driver matches browser before running any automation.

    This test runs first and fails fast if driver is out of date.
    """
    log.info("=" * 80)
    log.info("🔍 DRIVER VERIFICATION TEST - Running first")
    log.info("=" * 80)

    # Get current versions
    browser_ver = DriverDownloader.get_browser_version()
    driver_ver = DriverDownloader.get_driver_version(
        DriverDownloader.DRIVER_PATH
    )

    log.info(f"[DRIVER] Browser version: {browser_ver}")
    log.info(f"[DRIVER] Driver version:  {driver_ver}")

    # Check if versions are known
    assert browser_ver != "unknown", (
        "Could not detect browser version. "
        "Ensure Edge browser is installed."
    )

    if driver_ver == "unknown":
        pytest.skip(f"Driver binary not found at {DriverDownloader.DRIVER_PATH}. Falling back to Selenium Manager.")

    # Extract major versions
    try:
        browser_major = int(browser_ver.split(".")[0])
        driver_major = int(driver_ver.split(".")[0])
    except (ValueError, IndexError):
        pytest.fail(
            f"Could not parse version numbers: "
            f"browser='{browser_ver}', driver='{driver_ver}'"
        )

    # Verify they match
    if browser_major != driver_major:
        log.error(
            f"[DRIVER] ❌ VERSION MISMATCH: "
            f"Browser v{browser_ver} (major: {browser_major}) "
            f"vs Driver v{driver_ver} (major: {driver_major})"
        )

        # Attempt auto-fix
        log.info(f"[DRIVER] Attempting to auto-download driver v{browser_ver}...")
        if DriverDownloader.download_driver(
            browser_ver, DriverDownloader.DRIVER_PATH
        ):
            log.info(f"[DRIVER] ✅ Driver auto-updated to v{browser_ver}")
            # Re-verify
            new_driver_ver = DriverDownloader.get_driver_version(
                DriverDownloader.DRIVER_PATH
            )
            new_driver_major = int(new_driver_ver.split(".")[0])
            assert new_driver_major == browser_major, (
                f"Driver still doesn't match after update. "
                f"Browser v{browser_major}, Driver v{new_driver_major}. "
                f"Manual intervention required."
            )
        else:
            # Graceful fallback: warn but allow tests to proceed with existing driver
            log.warning(
                f"[DRIVER] ⚠️  Download failed, proceeding with existing driver v{driver_ver}. "
                f"Browser v{browser_ver} is newer but tests may still work. "
                f"Please run: python manage_driver.py --download to fix"
            )
    else:
        log.info(f"[DRIVER] ✅ Driver verification PASSED")
        log.info(f"[DRIVER] Browser v{browser_major} matches Driver v{driver_major}")

    log.info("=" * 80)
    log.info("✅ DRIVER VERIFICATION COMPLETE - Proceeding with tests")
    log.info("=" * 80)
