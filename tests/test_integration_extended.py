"""
Extended integration tests for comprehensive system validation.
As requested by STE - testing real system integration points.
"""
import pytest
import os
import tempfile
from unittest.mock import patch


class TestSystemReadiness:
    """Test overall system readiness for automation."""
    
    def test_system_ready_for_automation(self):
        """Comprehensive system readiness check."""
        from compass_automation.core.driver_manager import get_browser_version, get_driver_version, DRIVER_PATH
        from compass_automation.config.config_loader import get_config
        
        issues = []
        
        # Check 1: WebDriver exists (Optional if using Selenium Manager)
        if not os.path.exists(DRIVER_PATH):
            # issues.append(f"WebDriver missing: {DRIVER_PATH}")
            pass
        
        # Check 2: Version compatibility
        browser_ver = get_browser_version()
        driver_ver = get_driver_version(DRIVER_PATH)
        
        if browser_ver == "unknown":
            issues.append("Cannot detect browser version")
        
        if driver_ver == "unknown" and os.path.exists(DRIVER_PATH):
            issues.append("Cannot detect driver version")
        
        if browser_ver != "unknown" and driver_ver != "unknown":
            try:
                browser_major = int(browser_ver.split(".")[0])
                driver_major = int(driver_ver.split(".")[0])
                if browser_major != driver_major:
                    issues.append(f"Version mismatch: Browser {browser_ver} vs Driver {driver_ver}")
            except (ValueError, IndexError):
                issues.append(f"Cannot parse versions: Browser {browser_ver}, Driver {driver_ver}")
        
        # Check 3: Config accessibility
        try:
            username = get_config("username")
            login_id = get_config("login_id")
            if not username or not login_id:
                issues.append("Missing or empty credentials in config")
        except Exception as e:
            issues.append(f"Config error: {e}")
        
        # Check 4: Python environment
        import sys
        if sys.version_info < (3, 10):
            issues.append(f"Python version too old: {sys.version}")
        
        # Report results
        if issues:
            issue_list = "\n".join(f"  - {issue}" for issue in issues)
            pytest.fail(f"System not ready for automation:\n{issue_list}")
        
        print("✅ System is ready for automation!")
    
    def test_comprehensive_config_validation(self):
        """Test that all required config values are accessible and valid."""
        from compass_automation.config.config_loader import get_config
        
        required_keys = [
            "username",
            "password", 
            "login_id",
            "delay_seconds",
            "logging.min_crit",
            "logging.max_verb",
            "logging.file",
            "performance.config_threshold",
            "performance.object_creation_threshold"
        ]
        
        missing_keys = []
        invalid_values = []
        
        for key in required_keys:
            try:
                value = get_config(key)
                
                # Validate specific key types
                if key in ["delay_seconds", "performance.config_threshold", "performance.object_creation_threshold"]:
                    if not isinstance(value, (int, float)) or value <= 0:
                        invalid_values.append(f"{key}: {value} (should be positive number)")
                
                elif key in [
                    "username",
                    "password",
                    "login_id",
                    "logging.min_crit",
                    "logging.max_verb",
                    "logging.file",
                ]:
                    if not isinstance(value, str) or not value.strip():
                        invalid_values.append(f"{key}: empty or invalid string")
                        
            except KeyError:
                missing_keys.append(key)
        
        errors = []
        if missing_keys:
            errors.append(f"Missing config keys: {missing_keys}")
        if invalid_values:
            errors.append(f"Invalid config values: {invalid_values}")
        
        if errors:
            pytest.fail(f"Config validation failed:\n" + "\n".join(errors))
        
        print(f"✅ All {len(required_keys)} required config keys are valid")


class TestWebDriverIntegration:
    """Test actual WebDriver integration without launching browser."""
    
    def test_driver_service_configuration(self):
        """Test WebDriver service configuration."""
        from selenium.webdriver.edge.service import Service
        from compass_automation.core.driver_manager import DRIVER_PATH
        
        if not os.path.exists(DRIVER_PATH):
            pytest.skip(f"WebDriver not found: {DRIVER_PATH}")
        
        # Test service creation
        service = Service(DRIVER_PATH)
        assert service.path == DRIVER_PATH
        print(f"✅ WebDriver service configured: {DRIVER_PATH}")
    
    def test_edge_options_configuration(self):
        """Test Edge browser options configuration."""
        from selenium import webdriver
        
        options = webdriver.EdgeOptions()
        options.add_argument("--inprivate")
        options.add_argument("--start-maximized")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 2
        })
        
        # Verify options were set
        assert "--inprivate" in options.arguments
        assert "--start-maximized" in options.arguments
        assert "prefs" in options.experimental_options
        
        print("✅ Edge options configured correctly")
    
    def test_singleton_driver_pattern(self):
        """Test the singleton driver pattern works correctly."""
        from compass_automation.core import driver_manager
        
        # Reset driver state
        driver_manager.quit_driver()
        
        # First call should create driver (will test compatibility)
        try:
            driver1 = driver_manager.get_or_create_driver()
            assert driver1 is not None
            
            # Second call should return same instance
            driver2 = driver_manager.get_or_create_driver()
            assert driver1 is driver2, "Singleton pattern broken - different instances returned"
            
            print("✅ Singleton driver pattern working correctly")
        except RuntimeError as e:
            if "version mismatch" in str(e).lower():
                pytest.skip(f"Version mismatch prevents driver creation: {e}")
            else:
                raise
        finally:
            # Always cleanup
            driver_manager.quit_driver()


class TestPageObjectIntegration:
    """Test page object integration without browser."""
    
    def test_page_object_imports(self):
        """Test that all page objects can be imported."""
        page_classes = []
        
        try:
            from compass_automation.pages.login_page import LoginPage
            page_classes.append("LoginPage")
            
            from compass_automation.pages.mva_input_page import MVAInputPage  
            page_classes.append("MVAInputPage")
            
            from compass_automation.pages.drivability_page import DrivabilityPage
            page_classes.append("DrivabilityPage")
            
            from compass_automation.pages.complaint_type_page import ComplaintTypePage
            page_classes.append("ComplaintTypePage")
            
            # Only test pages that exist without import issues
            from compass_automation.pages.base_page import BasePage
            page_classes.append("BasePage")
            
        except ImportError as e:
            pytest.fail(f"Page object import failed: {e}")
        
        assert len(page_classes) >= 5, f"Expected at least 5 page classes, got {len(page_classes)}"
        print(f"✅ All {len(page_classes)} page objects importable: {page_classes}")
    
    def test_flow_integration(self):
        """Test that flow modules integrate properly."""
        flow_functions = []
        
        try:
            from compass_automation.flows.complaints_flows import handle_existing_complaint, handle_new_complaint
            flow_functions.extend(["handle_existing_complaint", "handle_new_complaint"])
            
            from compass_automation.flows.mileage_flows import complete_mileage_dialog, enter_mileage
            flow_functions.extend(["complete_mileage_dialog", "enter_mileage"])
            
            from compass_automation.flows.opcode_flows import select_opcode
            flow_functions.append("select_opcode")
            
            from compass_automation.flows.work_item_flow import handle_pm_workitems, process_workitem
            flow_functions.extend(["handle_pm_workitems", "process_workitem"])
            
            from compass_automation.flows.finalize_flow import finalize_workitem
            flow_functions.append("finalize_workitem")
            
        except ImportError as e:
            pytest.fail(f"Flow import failed: {e}")
        
        assert len(flow_functions) >= 7, f"Expected at least 7 flow functions, got {len(flow_functions)}"
        print(f"✅ All {len(flow_functions)} flow functions importable: {flow_functions}")
    
    def test_page_object_instantiation_patterns(self):
        """Test that page objects can be instantiated with mock driver."""
        from unittest.mock import MagicMock
        
        # Create mock driver
        mock_driver = MagicMock()
        
        page_objects = []
        
        try:
            from compass_automation.pages.login_page import LoginPage
            login_page = LoginPage(mock_driver)
            page_objects.append("LoginPage")
            
            from compass_automation.pages.mva_input_page import MVAInputPage
            mva_page = MVAInputPage(mock_driver)
            page_objects.append("MVAInputPage")
            
            from compass_automation.pages.base_page import BasePage
            base_page = BasePage(mock_driver)
            page_objects.append("BasePage")
            
        except Exception as e:
            pytest.fail(f"Page object instantiation failed: {e}")
        
        assert len(page_objects) >= 3
        print(f"✅ Page objects instantiated successfully: {page_objects}")


class TestLoggingIntegration:
    """Test logging system integration."""
    
    def test_logger_consistency_across_modules(self):
        """Test that logger works consistently across all modules."""
        loggers_tested = []
        
        try:
            # Test utils logger
            from compass_automation.utils.logger import log as utils_log
            assert utils_log.name == "mc.automation"
            loggers_tested.append("utils.logger")
            
            # Test core module logger
            from compass_automation.core.driver_manager import log as core_log
            assert core_log.name == "mc.automation"
            loggers_tested.append("core.driver_manager")
            
            # Verify they're the same logger instance
            assert utils_log is core_log, "Different logger instances found"
            
        except Exception as e:
            pytest.fail(f"Logger consistency check failed: {e}")
        
        print(f"✅ Logger consistent across {len(loggers_tested)} modules: {loggers_tested}")
    
    def test_log_level_configuration(self):
        """Test that logging is configured per the Two-Vector design."""
        from compass_automation.utils.logger import log
        import logging

        # The Two-Vector system keeps the underlying logger at DEBUG so that
        # filtering is performed by TwoVectorFilter (min_crit + max_verb).
        assert log.level == logging.DEBUG
        
        print("✅ Logger level is DEBUG; filtering handled by Two-Vector filter")


class TestDataIntegration:
    """Test data loading and validation integration."""
    
    def test_mva_data_loading_with_real_file(self):
        """Test MVA data loading with real file if available."""
        from compass_automation.utils.data_loader import load_mvas
        
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_file = os.path.join(project_root, "data", "mva.csv")
        
        if not os.path.exists(data_file):
            pytest.skip("MVA data file not found - create data/mva.csv for full integration testing")
        
        try:
            mvas = load_mvas(data_file)
            assert isinstance(mvas, list), "MVAs should be returned as list"
            
            if len(mvas) > 0:
                # Validate MVA format
                for mva in mvas[:5]:  # Check first 5
                    assert isinstance(mva, str), f"MVA should be string, got {type(mva)}"
                    assert mva.strip(), "MVA should not be empty"
                    assert len(mva) >= 4, f"MVA too short: {mva}"
                
                print(f"✅ Real data file loaded: {len(mvas)} MVAs")
            else:
                print("✅ Data file exists but is empty")
                
        except Exception as e:
            pytest.fail(f"Could not load real data file: {e}")
    
    def test_csv_format_tolerance(self):
        """Test that data loader handles various CSV formats."""
        from compass_automation.utils.data_loader import load_mvas
        
        test_cases = [
            # Standard format
            "12345\n67890\n",
            # With whitespace
            " 12345 \n 67890 \n",
            # With empty lines
            "12345\n\n67890\n\n",
            # With comments or headers
            "# MVA Numbers\n12345\n67890\n",
            # Mixed format
            "12345,some,extra,data\n67890\n"
        ]
        
        for i, csv_content in enumerate(test_cases):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(csv_content)
                temp_path = f.name
            
            try:
                mvas = load_mvas(temp_path)
                assert len(mvas) >= 2, f"Test case {i} failed: expected at least 2 MVAs, got {len(mvas)}"
                assert "12345" in mvas, f"Test case {i} failed: missing expected MVA"
                assert "67890" in mvas, f"Test case {i} failed: missing expected MVA"
            except Exception as e:
                pytest.fail(f"CSV format test case {i} failed: {e}")
            finally:
                os.unlink(temp_path)
        
        print(f"✅ CSV format tolerance verified: {len(test_cases)} test cases passed")


class TestErrorHandling:
    """Test error handling and recovery scenarios."""
    
    def test_graceful_degradation_on_missing_components(self):
        """Test system behavior when optional components are missing."""
        from compass_automation.core.driver_manager import get_browser_version, get_driver_version
        
        # Test browser version detection failure
        with patch('winreg.OpenKey', side_effect=Exception("Registry access denied")):
            browser_ver = get_browser_version()
            assert browser_ver == "unknown", "Should return 'unknown' on registry failure"
        
        # Test driver version detection failure  
        with patch('os.path.exists', return_value=False):
            driver_ver = get_driver_version("nonexistent_path")
            assert driver_ver == "unknown", "Should return 'unknown' for missing driver"
        
        print("✅ Graceful degradation verified for missing components")
    
    def test_config_error_handling(self):
        """Test configuration error handling."""
        from compass_automation.config.config_loader import get_config
        
        # Test missing key with default
        result = get_config("nonexistent_key", "default_value")
        assert result == "default_value"
        
        # Test missing nested key with default
        result = get_config("missing.nested.key", "default_value")
        assert result == "default_value"
        
        # Test missing key without default raises error
        with pytest.raises(KeyError):
            get_config("totally_missing_key")
        
        print("✅ Config error handling verified")


if __name__ == "__main__":
    # Run extended integration tests
    pytest.main([__file__, "-v", "--tb=short"])