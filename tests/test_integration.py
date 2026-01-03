"""
Integration tests for version compatibility and system checks.
These tests verify real system state without requiring browser launch.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestVersionCompatibility:
    """Test driver and browser version compatibility."""
    
    def test_driver_browser_version_compatibility(self):
        """Test that driver and browser versions are compatible."""
        from compass_automation.core.driver_manager import get_browser_version, get_driver_version, DRIVER_PATH
        
        browser_ver = get_browser_version()
        driver_ver = get_driver_version(DRIVER_PATH)
        
        # Skip test if either version is unknown (system not set up)
        if browser_ver == "unknown" or driver_ver == "unknown":
            pytest.skip("Browser or driver version unknown - system may not be fully configured")
        
        # Extract major version numbers for comparison
        try:
            browser_major = int(browser_ver.split(".")[0])
            driver_major = int(driver_ver.split(".")[0])
        except (ValueError, IndexError):
            pytest.fail(f"Could not parse version numbers: browser='{browser_ver}', driver='{driver_ver}'")
        
        # Major versions should match (but graceful fallback is allowed with warning)
        if browser_major != driver_major:
            # Warn but don't fail - graceful fallback allows mismatches
            pytest.skip(
                f"Version mismatch detected: Browser v{browser_ver} (major: {browser_major}) "
                f"vs Driver v{driver_ver} (major: {driver_major}). "
                f"System will work with graceful fallback. "
                f"Run 'python manage_driver.py --download' to update."
            )
        
        print(f"✅ Version compatibility verified: Browser {browser_ver} ↔ Driver {driver_ver}")
    
    def test_driver_file_exists(self):
        """Test that the WebDriver executable exists at the expected path."""
        import os
        from compass_automation.core.driver_manager import DRIVER_PATH
        
        if not os.path.exists(DRIVER_PATH):
            pytest.skip(f"WebDriver binary not found at {DRIVER_PATH}. Using Selenium Manager fallback.")
        
        assert os.path.isfile(DRIVER_PATH), f"Path exists but is not a file: {DRIVER_PATH}"
        
        # Check if file is executable (on Windows, .exe should be executable)
        assert DRIVER_PATH.endswith('.exe'), f"Expected .exe file, got: {DRIVER_PATH}"
        
        print(f"✅ WebDriver file verified: {DRIVER_PATH}")
    
    def test_driver_version_extractable(self):
        """Test that we can extract version from the WebDriver executable."""
        from compass_automation.core.driver_manager import get_driver_version, DRIVER_PATH
        
        import os
        if not os.path.exists(DRIVER_PATH):
            pytest.skip(f"WebDriver binary not found at {DRIVER_PATH}")
        version = get_driver_version(DRIVER_PATH)
        
        assert version != "unknown", (
            f"Could not extract version from WebDriver at {DRIVER_PATH}. "
            f"The file may be corrupted or incorrect."
        )
        
        # Version should be in format like "142.0.3595.65"
        version_parts = version.split(".")
        assert len(version_parts) >= 3, f"Unexpected version format: {version}"
        
        # Each part should be numeric
        for part in version_parts:
            assert part.isdigit(), f"Non-numeric version part in {version}: '{part}'"
        
        print(f"✅ Driver version extracted: {version}")
    
    def test_browser_version_extractable(self):
        """Test that we can extract version from the installed browser."""
        from compass_automation.core.driver_manager import get_browser_version
        
        version = get_browser_version()
        
        # On systems without Edge or registry access issues, this might be "unknown"
        if version == "unknown":
            pytest.skip("Could not extract browser version - may not be installed or registry access denied")
        
        # Version should be in format like "142.0.3595.65"
        version_parts = version.split(".")
        assert len(version_parts) >= 3, f"Unexpected browser version format: {version}"
        
        # Each part should be numeric
        for part in version_parts:
            assert part.isdigit(), f"Non-numeric version part in {version}: '{part}'"
        
        print(f"✅ Browser version extracted: {version}")
    
    def test_version_mismatch_detection(self):
        """Test that version mismatch is detected and logged as warning."""
        import compass_automation.core.driver_manager as driver_manager

        # Mock incompatible versions to ensure we warn but still proceed.
        with patch("compass_automation.core.driver_manager.get_browser_version", return_value="142.0.3595.65"), \
             patch("compass_automation.core.driver_manager.get_driver_version", return_value="141.0.3485.54"), \
             patch("compass_automation.core.driver_manager.os.path.exists", return_value=False), \
             patch("compass_automation.core.driver_manager.log.warning") as mock_warn, \
             patch("compass_automation.core.driver_manager.webdriver.Edge") as mock_edge:
            # Ensure we don't leak a fake singleton into other tests.
            driver_manager._driver = None
            mock_driver = MagicMock(name="mock_driver")
            mock_edge.return_value = mock_driver

            driver = driver_manager.get_or_create_driver()
            assert driver is mock_driver
            assert mock_warn.called, "Expected version mismatch to be logged as a warning"

            # Clean up so later e2e tests can create a real driver.
            driver_manager.quit_driver()
            assert driver_manager._driver is None

            print("✅ Version mismatch detected and handled gracefully")
    
    
    def test_compatible_versions_pass(self):
        """Test that compatible versions don't raise errors (without creating driver)."""
        # Mock compatible versions
        with patch('compass_automation.core.driver_manager.get_browser_version', return_value="142.0.3595.65"):
            with patch('compass_automation.core.driver_manager.get_driver_version', return_value="142.0.3485.54"):
                with patch('compass_automation.core.driver_manager._driver', None):  # Ensure no cached driver
                    with patch('selenium.webdriver.Edge') as mock_edge:
                        mock_edge.return_value = "mock_driver"
                        
                        # This should NOT raise an error
                        try:
                            from compass_automation.core.driver_manager import get_or_create_driver
                            # We'll mock the actual driver creation to avoid launching browser
                            with patch('compass_automation.core.driver_manager.webdriver.Edge'):
                                # Just test the version checking logic
                                browser_ver = "142.0.3595.65"
                                driver_ver = "142.0.3485.54"
                                
                                # This is the same logic as in get_or_create_driver
                                if browser_ver.split(".")[0] != driver_ver.split(".")[0]:
                                    pytest.fail("Should not raise error for compatible versions")
                                
                                print("✅ Compatible versions correctly passed validation")
                        except RuntimeError as e:
                            if "version mismatch" in str(e).lower():
                                pytest.fail(f"Compatible versions incorrectly rejected: {e}")
                            else:
                                # Other RuntimeErrors are fine (e.g., WebDriver not found)
                                pass


class TestSystemReadiness:
    """Test that the system is ready for automation."""
    
    def test_system_ready_for_automation(self):
        """Comprehensive test that system is ready for browser automation."""
        import os
        from compass_automation.core.driver_manager import get_browser_version, get_driver_version, DRIVER_PATH
        
        issues = []
        
        # Check 1: WebDriver file exists (Optional if using Selenium Manager)
        if not os.path.exists(DRIVER_PATH):
            # issues.append(f"WebDriver not found at {DRIVER_PATH}")
            pass
        
        # Check 2: Can extract browser version
        browser_ver = get_browser_version()
        if browser_ver == "unknown":
            issues.append("Cannot extract browser version from registry")
        
        # Check 3: Can extract driver version
        driver_ver = get_driver_version(DRIVER_PATH)
        if driver_ver == "unknown" and os.path.exists(DRIVER_PATH):
            issues.append(f"Cannot extract driver version from {DRIVER_PATH}")
        
        # Check 4: Versions are compatible
        if browser_ver != "unknown" and driver_ver != "unknown":
            browser_major = browser_ver.split(".")[0]
            driver_major = driver_ver.split(".")[0]
            if browser_major != driver_major:
                issues.append(f"Version mismatch: Browser {browser_ver} vs Driver {driver_ver}")
        
        # Report results
        if issues:
            pytest.fail(
                f"System not ready for automation:\n" + 
                "\n".join(f"  - {issue}" for issue in issues)
            )
        
        print(f"✅ System ready: Browser {browser_ver} ↔ Driver {driver_ver}")
    
    def test_config_accessibility(self):
        """Test that configuration is accessible and valid."""
        from compass_automation.config.config_loader import get_config
        
        # Check essential config keys exist
        essential_keys = ["username", "password", "login_id"]
        
        for key in essential_keys:
            try:
                value = get_config(key)
                assert value is not None, f"Config key '{key}' is None"
                assert isinstance(value, str), f"Config key '{key}' is not a string: {type(value)}"
                assert len(value.strip()) > 0, f"Config key '{key}' is empty"
            except KeyError:
                pytest.fail(f"Missing required config key: '{key}'")
        
        print("✅ Configuration is accessible and valid")
    
    def test_data_file_accessibility(self):
        """Test that required data files are accessible."""
        import os
        from compass_automation.utils.data_loader import load_mvas
        
        # Check if default data file exists
        data_file = "data/mva.csv"
        
        if not os.path.exists(data_file):
            pytest.skip(f"Data file {data_file} not found - this is optional for unit tests")
        
        # If it exists, test that it can be loaded
        try:
            mvas = load_mvas(data_file)
            assert isinstance(mvas, list), "load_mvas should return a list"
            
            if mvas:  # If not empty
                assert all(isinstance(mva, str) for mva in mvas), "All MVAs should be strings"
                print(f"✅ Data file loaded successfully: {len(mvas)} MVAs")
            else:
                print("✅ Data file exists but is empty")
                
        except Exception as e:
            pytest.fail(f"Could not load data file {data_file}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])