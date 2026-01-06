"""
Quick smoke tests for running specific functionality.
These tests can be run frequently during development.
"""
import pytest
import tempfile
import os


class TestQuickSmoke:
    """Quick smoke tests for core functionality."""
    
    def test_project_structure_intact(self):
        """Verify key project files exist."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        essential_files = [
            "src/compass_automation/config/config.json",
            "src/compass_automation/core/driver_manager.py", 
            "src/compass_automation/utils/data_loader.py",
            "src/compass_automation/utils/logger.py",
            "src/compass_automation/pages/complaint.py",
            "src/compass_automation/pages/work_item.py",
            "src/compass_automation/pages/vehicle.py"
        ]
        
        for file_path in essential_files:
            full_path = os.path.join(project_root, file_path)
            assert os.path.exists(full_path), f"Missing essential file: {file_path}"
    
    def test_all_imports_work(self):
        """Test that all major modules can be imported without errors."""
        try:
            # Core imports
            from compass_automation.core import driver_manager
            from compass_automation.config import config_loader
            
            # Utils imports  
            from compass_automation.utils import data_loader, logger
            
            # Pages imports
            from compass_automation.pages import complaint, work_item, vehicle
            
            # All imports successful
            assert True
            
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
    
    def test_config_basic_access(self):
        """Test basic config access works."""
        from compass_automation.config.config_loader import get_config
        
        # These keys should exist in the config
        username = get_config("username")
        login_id = get_config("login_id")
        
        assert isinstance(username, str)
        assert isinstance(login_id, str)
        assert len(username) > 0
        assert len(login_id) > 0
    
    def test_logger_basic_functionality(self):
        """Test that logging works without errors."""
        import io
        import logging

        from compass_automation.utils.logger import TwoVectorFormatter, log

        # Don't pollute the shared automation.log during unit/smoke tests.
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(TwoVectorFormatter())

        old_handlers = list(log.handlers)
        old_filters = list(getattr(log, "filters", []))
        old_propagate = log.propagate
        try:
            log.handlers = []
            log.filters = []
            log.propagate = False
            log.addHandler(handler)

            # These should not raise exceptions
            log.debug("Test debug message")
            log.info("Test info message")
            log.warning("Test warning message")
        finally:
            log.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass
            log.handlers = old_handlers
            log.filters = old_filters
            log.propagate = old_propagate

        assert log.name == "mc.automation"
    
    def test_data_loader_basic_functionality(self):
        """Test basic data loading functionality."""
        from compass_automation.utils.data_loader import load_mvas
        
        # Create a simple test CSV
        csv_content = "12345\n67890\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            mvas = load_mvas(temp_path)
            assert len(mvas) == 2
            assert "12345" in mvas
            assert "67890" in mvas
        finally:
            os.unlink(temp_path)
    
    def test_domain_objects_creation(self):
        """Test that domain objects can be created."""
        from compass_automation.pages.complaint import Complaint
        from compass_automation.pages.work_item import WorkItem
        from compass_automation.pages.vehicle import Vehicle
        
        # Should not raise exceptions
        complaint = Complaint(id="1", type="PM", status="Open")
        work_item = WorkItem(id="2", type="PM", status="Complete")
        vehicle = Vehicle(mva="12345")
        
        assert complaint.id == "1"
        assert work_item.id == "2"
        assert vehicle.mva == "12345"
    
    def test_driver_manager_constants(self):
        """Test that driver manager constants are defined."""
        from compass_automation.core.driver_manager import DRIVER_PATH
        
        assert isinstance(DRIVER_PATH, str)
        assert "msedgedriver.exe" in DRIVER_PATH
    
    def test_version_check_functions_exist(self):
        """Test that version checking functions exist and are callable."""
        from compass_automation.core.driver_manager import get_browser_version, get_driver_version
        
        # These functions should exist and be callable
        assert callable(get_browser_version)
        assert callable(get_driver_version)
        
        # They should return strings (even if "unknown")
        browser_ver = get_browser_version()
        assert isinstance(browser_ver, str)


class TestPerformance:
    """Basic performance checks for fast functions."""
    
    def test_config_loading_is_fast(self):
        """Test that config loading is fast (cached)."""
        import time
        from compass_automation.config.config_loader import get_config
        
        start_time = time.time()
        
        # Do multiple config accesses
        for _ in range(100):
            get_config("username")
            get_config("login_id")
            get_config("delay_seconds", 5)
        
        elapsed = time.time() - start_time
        
        # Should be very fast since config is loaded once at import
        assert elapsed < 0.1, f"Config access too slow: {elapsed:.3f}s"
    
    def test_domain_object_creation_is_fast(self):
        """Test that domain object creation is fast."""
        import time
        from compass_automation.pages.complaint import Complaint
        
        start_time = time.time()
        
        # Create many objects
        for i in range(1000):
            Complaint(id=str(i), type="PM", status="Open")
        
        elapsed = time.time() - start_time
        
        # Should be very fast
        assert elapsed < 0.1, f"Object creation too slow: {elapsed:.3f}s"


class TestDataValidation:
    """Test data validation and sanitization."""
    
    def test_mva_data_types(self):
        """Test that MVA data is properly typed."""
        from compass_automation.utils.data_loader import load_mvas
        
        csv_content = "12345\n67890\n11111\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            mvas = load_mvas(temp_path)
            
            # All MVAs should be strings
            for mva in mvas:
                assert isinstance(mva, str)
                # Should be numeric strings
                assert mva.isdigit()
                # Should have reasonable length
                assert 1 <= len(mva) <= 20
        finally:
            os.unlink(temp_path)
    
    def test_status_validation(self):
        """Test that status values are properly validated."""
        from compass_automation.pages.complaint import Complaint
        from compass_automation.pages.work_item import WorkItem
        
        # Test valid statuses
        valid_complaint_statuses = ["Open", "Closed", "OPEN", "open", "closed"]
        valid_work_item_statuses = ["Open", "Complete", "OPEN", "open", "complete"]
        
        for status in valid_complaint_statuses:
            complaint = Complaint(id="1", type="PM", status=status)
            # Should not raise exceptions
            assert isinstance(complaint.is_open(), bool)
            assert isinstance(complaint.is_closed(), bool)
        
        for status in valid_work_item_statuses:
            work_item = WorkItem(id="1", type="PM", status=status)
            # Should not raise exceptions  
            assert isinstance(work_item.is_open(), bool)
            assert isinstance(work_item.is_complete(), bool)


if __name__ == "__main__":
    # Quick run command
    pytest.main([__file__, "-v", "--tb=short"])