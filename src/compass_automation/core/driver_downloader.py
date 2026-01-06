"""
Automatic Edge WebDriver downloader and manager.

This module automatically downloads and maintains the correct version of msedgedriver.exe
to match the installed Edge browser version.
"""

import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Optional
from urllib.request import urlopen

from compass_automation.utils.logger import TwoVectorLogger, Verbosity, log


from compass_automation.utils.project_paths import ProjectPaths


class DriverDownloader:
    """Automatically downloads and manages Edge WebDriver versions."""

    DRIVER_DOWNLOAD_URL = "https://edgedriver.microsoft.com/download/{version}"
    DRIVER_PATH = ProjectPaths.get_project_root() / "msedgedriver.exe"

    @staticmethod
    def get_browser_version() -> str:
        """Return installed Edge browser version from Windows registry."""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Edge\BLBeacon"
            )
            value, _ = winreg.QueryValueEx(key, "version")
            return value
        except Exception as e:
            TwoVectorLogger(log, source="DRIVER").error_v(
                Verbosity.MED,
                "Failed to get browser version from registry: %s",
                e,
            )
            return "unknown"

    @staticmethod
    def get_driver_version(driver_path: Path) -> str:
        """Return Edge WebDriver version (e.g., 143.0.x.x)."""
        if not driver_path.exists():
            return "unknown"
        try:
            output = subprocess.check_output(
                [str(driver_path), "--version"],
                text=True,
                timeout=5
            )
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
            if match:
                return match.group(1)
            return "unknown"
        except Exception as e:
            TwoVectorLogger(log, source="DRIVER").error_v(
                Verbosity.MED,
                "Failed to extract driver version: %s",
                e,
            )
            return "unknown"

    @staticmethod
    def download_driver(version: str, target_path: Path) -> bool:
        """
        Download Edge WebDriver for the given version.

        Args:
            version: Driver version (e.g., '143.0.3650.80')
            target_path: Where to save msedgedriver.exe

        Returns:
            True if successful, False otherwise
        """
        import socket
        
        try:
            driver_log = TwoVectorLogger(log, source="DRIVER")
            url = DriverDownloader.DRIVER_DOWNLOAD_URL.format(version=version)
            driver_log.info_v(Verbosity.MIN, "Downloading driver v%s from %s", version, url)

            # Create temp directory for extraction
            temp_dir = target_path.parent / ".driver_temp"
            temp_dir.mkdir(exist_ok=True)

            # Download zip file with retry logic
            zip_path = temp_dir / "msedgedriver.zip"
            driver_log.info_v(Verbosity.MED, "Downloading to %s", zip_path)

            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with urlopen(url, timeout=30) as response:
                        with open(zip_path, "wb") as out_file:
                            out_file.write(response.read())
                    break  # Success, exit retry loop
                    
                except (socket.gaierror, ConnectionError, TimeoutError) as net_error:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = 2 ** retry_count  # Exponential backoff
                        log.warning(
                            "Network error (attempt %s/%s): %s. Retrying in %s seconds...",
                            retry_count,
                            max_retries,
                            net_error,
                            wait_time,
                        )
                        time.sleep(wait_time)
                    else:
                        raise

            driver_log.info_v(Verbosity.MIN, "Download complete, extracting...")

            # Extract the driver
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Extract all files
                zip_ref.extractall(temp_dir)

                # Find msedgedriver.exe in the extracted files
                for root, dirs, files in os.walk(temp_dir):
                    if "msedgedriver.exe" in files:
                        extracted_driver = Path(root) / "msedgedriver.exe"

                        # Backup existing driver if present
                        if target_path.exists():
                            backup_path = target_path.with_stem(
                                f"{target_path.stem}_backup"
                            )
                            driver_log.info_v(Verbosity.MED, "Backing up existing driver to %s", backup_path)
                            shutil.copy2(target_path, backup_path)

                        # Move extracted driver to target location
                        shutil.move(str(extracted_driver), str(target_path))
                        driver_log.info_v(Verbosity.MIN, "Driver installed to %s", target_path)

                        # Cleanup temp directory
                        shutil.rmtree(temp_dir, ignore_errors=True)

                        return True

            driver_log.error_v(Verbosity.MIN, "msedgedriver.exe not found in downloaded zip")
            return False

        except Exception as e:
            driver_log = TwoVectorLogger(log, source="DRIVER")
            driver_log.error_v(Verbosity.MIN, "Download failed: %s", e)
            # Provide helpful troubleshooting info
            driver_log.error_v(
                Verbosity.MED,
                "Troubleshooting: Check network/firewall, or manually download from https://edgedriver.microsoft.com/download/%s",
                version,
            )
            return False

    @staticmethod
    def ensure_driver_ready() -> bool:
        """
        Ensure the correct version of msedgedriver.exe is present.

        Automatically downloads and updates if needed.

        Returns:
            True if driver is ready, False otherwise
        """
        browser_ver = DriverDownloader.get_browser_version()

        if browser_ver == "unknown":
            driver_log = TwoVectorLogger(log, source="DRIVER")
            driver_log.warning_v(Verbosity.MED, "Could not detect browser version - skipping auto-update")
            return DriverDownloader.DRIVER_PATH.exists()

        driver_ver = DriverDownloader.get_driver_version(DriverDownloader.DRIVER_PATH)

        driver_log = TwoVectorLogger(log, source="DRIVER")
        driver_log.info_v(Verbosity.MIN, "Browser v%s, Driver v%s", browser_ver, driver_ver)

        # Compare major versions
        browser_major = browser_ver.split(".")[0]
        driver_major = driver_ver.split(".")[0] if driver_ver != "unknown" else "0"

        if browser_major == driver_major:
            driver_log.info_v(Verbosity.MIN, "Driver version matches browser")
            return True

        # Version mismatch - attempt to download correct version
        driver_log.warning_v(Verbosity.MED, "Version mismatch: browser=%s, driver=%s", browser_ver, driver_ver)
        driver_log.info_v(Verbosity.MIN, "Attempting to download driver v%s...", browser_ver)

        if DriverDownloader.download_driver(browser_ver, DriverDownloader.DRIVER_PATH):
            driver_log.info_v(Verbosity.MIN, "Driver updated to v%s", browser_ver)
            return True
        else:
            # Download failed, but let's check if existing driver is usable
            if DriverDownloader.DRIVER_PATH.exists():
                log.warning(
                    "Download failed, but existing driver found. System may work with v%s, but best practice is to update. Manual download: https://edgedriver.microsoft.com/download/%s",
                    driver_ver,
                    browser_ver,
                )
                return True  # Proceed with caution
            else:
                log.error(
                    "Failed to download driver v%s and no existing driver found. Manual download required: https://edgedriver.microsoft.com/download/%s",
                    browser_ver,
                    browser_ver,
                )
                return False


def ensure_driver() -> bool:
    """
    Module-level function to ensure driver is ready.

    Call this early in your code (e.g., at import time) to auto-update the driver.
    """
    return DriverDownloader.ensure_driver_ready()


# Auto-ensure driver on module import (optional - can be disabled)
# Uncomment the line below to auto-check/download driver when this module is imported
# ensure_driver()
