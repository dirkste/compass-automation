"""
Fast unit tests for compass-automation project.
These tests run without Selenium/browser dependencies.
"""
import pytest
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock


class TestConfigLoader:
    """Test config/config_loader.py functionality."""
    
    def test_get_config_existing_key(self):
        """Test retrieving an existing config key."""
        from config.config_loader import get_config
        
        # Test a key we know exists
        username = get_config("username")
        assert username is not None
        assert isinstance(username, str)
    
    def test_get_config_with_default(self):
        """Test retrieving non-existent key with default value."""
        from config.config_loader import get_config
        
        result = get_config("nonexistent_key", "default_value")
        assert result == "default_value"
    
    def test_get_config_missing_key_no_default(self):
        """Test that missing key without default raises KeyError."""
        from config.config_loader import get_config
        
        with pytest.raises(KeyError):
            get_config("totally_missing_key")


class TestDataLoader:
    """Test utils/data_loader.py functionality."""
    
    def test_load_mvas_basic(self):
        """Test loading MVAs from a temporary CSV file."""
        from utils.data_loader import load_mvas
        
        # Create temporary CSV content
        csv_content = "54252855\n56035512\n51594211\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            mvas = load_mvas(temp_path)
            assert len(mvas) == 3
            assert "54252855" in mvas
            assert "56035512" in mvas
            assert "51594211" in mvas
        finally:
            os.unlink(temp_path)
    
    def test_load_mvas_with_comments(self):
        """Test loading MVAs while filtering out comment lines."""
        from utils.data_loader import load_mvas
        
        csv_content = "#mva\n54252855\n#comment\n56035512\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            mvas = load_mvas(temp_path)
            assert len(mvas) == 2
            assert "54252855" in mvas
            assert "56035512" in mvas
            assert "#mva" not in mvas
            assert "#comment" not in mvas
        finally:
            os.unlink(temp_path)
    
    def test_load_mvas_empty_file(self):
        """Test loading from empty CSV file."""
        from utils.data_loader import load_mvas
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            mvas = load_mvas(temp_path)
            assert len(mvas) == 0
        finally:
            os.unlink(temp_path)


class TestDomainObjects:
    """Test domain objects in pages/ directory."""
    
    def test_complaint_creation(self):
        """Test Complaint object creation and methods."""
        from pages.complaint import Complaint
        
        complaint = Complaint(
            id="123",
            type="PM",
            status="Open",
            created_at=datetime(2025, 1, 1)
        )
        
        assert complaint.id == "123"
        assert complaint.type == "PM"
        assert complaint.is_open()
        assert not complaint.is_closed()
        assert complaint.age_in_days() is not None
    
    def test_work_item_creation(self):
        """Test WorkItem object creation and methods."""
        from pages.work_item import WorkItem
        
        work_item = WorkItem(
            id="456",
            type="PM",
            status="Complete",
            completed_at=datetime(2025, 1, 1)
        )
        
        assert work_item.id == "456"
        assert work_item.type == "PM"
        assert not work_item.is_open()
        assert work_item.is_complete()
        assert work_item.age_in_days() is not None
    
    def test_vehicle_creation(self):
        """Test Vehicle object creation and methods."""
        from pages.vehicle import Vehicle
        
        vehicle = Vehicle(
            mva="54252855",
            plate="ABC123",
            purchase_date=datetime(2024, 1, 1)
        )
        
        assert vehicle.mva == "54252855"
        assert vehicle.plate == "ABC123"
        assert vehicle.age_in_days() is not None


class TestDriverManagerVersions:
    """Test driver_manager.py version checking logic (without browser)."""
    
    @patch('subprocess.check_output')
    def test_get_driver_version_success(self, mock_subprocess):
        """Test successful driver version extraction."""
        from core.driver_manager import get_driver_version
        
        # Mock subprocess output
        mock_subprocess.return_value = "Microsoft Edge WebDriver 142.0.3595.65 (abc123)"
        
        with patch('os.path.exists', return_value=True):
            version = get_driver_version("fake_path")
            assert version == "142.0.3595.65"
    
    @patch('subprocess.check_output')
    def test_get_driver_version_file_not_found(self, mock_subprocess):
        """Test driver version when file doesn't exist."""
        from core.driver_manager import get_driver_version
        
        with patch('os.path.exists', return_value=False):
            version = get_driver_version("nonexistent_path")
            assert version == "unknown"
    
    @patch('subprocess.check_output')
    def test_get_driver_version_command_fails(self, mock_subprocess):
        """Test driver version when command fails."""
        from core.driver_manager import get_driver_version
        
        mock_subprocess.side_effect = Exception("Command failed")
        
        with patch('os.path.exists', return_value=True):
            version = get_driver_version("fake_path")
            assert version == "unknown"
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    def test_get_browser_version_success(self, mock_query, mock_open):
        """Test successful browser version extraction."""
        from core.driver_manager import get_browser_version
        
        mock_query.return_value = ("142.0.3595.65", None)
        
        version = get_browser_version()
        assert version == "142.0.3595.65"
    
    @patch('winreg.OpenKey')
    def test_get_browser_version_registry_error(self, mock_open):
        """Test browser version when registry access fails."""
        from core.driver_manager import get_browser_version
        
        mock_open.side_effect = Exception("Registry error")
        
        version = get_browser_version()
        assert version == "unknown"


class TestLoggerConfiguration:
    """Test logger configuration and color formatting."""
    
    def test_color_formatter_creation(self):
        """Test ColorFormatter can be created."""
        from utils.logger import ColorFormatter
        
        formatter = ColorFormatter("[%(levelname)s] %(message)s")
        assert formatter is not None
    
    def test_logger_instance_exists(self):
        """Test that the logger instance is created."""
        from utils.logger import log
        
        assert log is not None
        assert log.name == "mc.automation"
    
    def test_color_formatter_format(self):
        """Test ColorFormatter.format method."""
        import logging
        from utils.logger import ColorFormatter
        
        formatter = ColorFormatter("%(levelname)s: %(message)s")
        
        # Create a test log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert "INFO: Test message" in formatted


class TestHelperFunctions:
    """Test utility helper functions that don't require Selenium."""
    
    def test_data_loader_strip_whitespace(self):
        """Test that data loader strips whitespace from MVAs."""
        from utils.data_loader import load_mvas
        
        csv_content = " 54252855 \n  56035512  \n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            mvas = load_mvas(temp_path)
            assert len(mvas) == 2
            assert "54252855" in mvas  # Should be stripped
            assert "56035512" in mvas  # Should be stripped
            assert " 54252855 " not in mvas  # Whitespace should be gone
        finally:
            os.unlink(temp_path)


# Quick smoke tests for import validation
class TestImports:
    """Test that all major modules can be imported without errors."""
    
    def test_config_imports(self):
        """Test config module imports."""
        from config import config_loader
        assert hasattr(config_loader, 'get_config')
    
    def test_utils_imports(self):
        """Test utils module imports."""
        from utils import data_loader, logger
        assert hasattr(data_loader, 'load_mvas')
        assert hasattr(logger, 'log')
    
    def test_pages_imports(self):
        """Test pages module imports."""
        from pages import complaint, work_item, vehicle
        assert hasattr(complaint, 'Complaint')
        assert hasattr(work_item, 'WorkItem')
        assert hasattr(vehicle, 'Vehicle')
    
    def test_core_imports(self):
        """Test core module imports."""
        from core import driver_manager
        assert hasattr(driver_manager, 'get_browser_version')
        assert hasattr(driver_manager, 'get_driver_version')


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_unit_fast.py -v
    pytest.main([__file__, "-v"])