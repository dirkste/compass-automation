#!/usr/bin/env python3
"""
Command-line tool to manage Edge WebDriver.

Usage:
    python manage_driver.py              # Check and auto-update driver
    python manage_driver.py --check      # Check current versions
    python manage_driver.py --download   # Force download current version
    python manage_driver.py --help       # Show help
"""

import argparse
import sys
from pathlib import Path

# Add project root and src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from compass_automation.core.driver_downloader import DriverDownloader
from compass_automation.utils.logger import log


def check_versions():
    """Display current browser and driver versions."""
    print("\n" + "=" * 70)
    print("EDGE DRIVER STATUS CHECK")
    print("=" * 70)

    browser_ver = DriverDownloader.get_browser_version()
    driver_ver = DriverDownloader.get_driver_version(
        DriverDownloader.DRIVER_PATH
    )

    print(f"Browser Version: {browser_ver}")
    print(f"Driver Version:  {driver_ver}")
    print(f"Driver Path:     {DriverDownloader.DRIVER_PATH}")

    if browser_ver == "unknown":
        print("\n⚠️  Could not detect browser version")
        return False

    if driver_ver == "unknown":
        print("\n❌ Driver not found or cannot determine version")
        return False

    browser_major = browser_ver.split(".")[0]
    driver_major = driver_ver.split(".")[0]

    if browser_major == driver_major:
        print(f"\n✅ MATCH: Browser and driver versions are compatible!")
        return True
    else:
        print(f"\n❌ MISMATCH: Browser v{browser_major} vs Driver v{driver_major}")
        return False


def download_driver():
    """Download the correct driver version."""
    browser_ver = DriverDownloader.get_browser_version()

    if browser_ver == "unknown":
        print("❌ Could not detect browser version - cannot download driver")
        return False

    print(f"\n📥 Downloading Edge WebDriver v{browser_ver}...")

    if DriverDownloader.download_driver(
        browser_ver, DriverDownloader.DRIVER_PATH
    ):
        print(f"✅ Successfully downloaded and installed driver v{browser_ver}")
        return True
    else:
        print(f"❌ Failed to download driver v{browser_ver}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Edge WebDriver for Compass Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_driver.py              # Auto-check and update if needed
  python manage_driver.py --check      # Check versions only
  python manage_driver.py --download   # Force download current version
        """
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current browser and driver versions"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Force download the current browser version's driver"
    )

    args = parser.parse_args()

    if args.check:
        success = check_versions()
    elif args.download:
        success = download_driver()
    else:
        # Default: auto-ensure (check and download if needed)
        print("\n" + "=" * 70)
        print("COMPASS AUTOMATION - DRIVER MANAGER")
        print("=" * 70)
        success = DriverDownloader.ensure_driver_ready()

        if success:
            print("\n✅ Driver is ready for automation")
        else:
            print("\n❌ Driver setup failed")

    print()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
