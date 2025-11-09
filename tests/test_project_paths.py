"""
Test suite for utils.project_paths module.

Tests the ProjectPaths utility class to ensure correct path resolution
across different environments and validate all path management functionality.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from utils.project_paths import ProjectPaths, get_config_file_path, get_data_file_path, get_project_root_path


class TestProjectPaths:
    """Test cases for ProjectPaths utility class."""
    
    def setup_method(self):
        """Reset ProjectPaths cache before each test."""
        ProjectPaths._project_root = None
    
    def test_get_project_root_returns_path_object(self):
        """Test that get_project_root returns a Path object."""
        root = ProjectPaths.get_project_root()
        assert isinstance(root, Path)
        assert root.is_absolute()
    
    def test_get_project_root_is_cached(self):
        """Test that get_project_root caches the result."""
        root1 = ProjectPaths.get_project_root()
        root2 = ProjectPaths.get_project_root()
        assert root1 is root2  # Same object reference due to caching
    
    def test_get_project_root_points_to_correct_directory(self):
        """Test that project root contains expected project files."""
        root = ProjectPaths.get_project_root()
        
        # Verify it contains key project structure
        assert (root / "utils").is_dir()
        assert (root / "config").is_dir()
        assert (root / "pages").is_dir()
        assert (root / "tests").is_dir()
        assert (root / "utils" / "project_paths.py").is_file()
    
    def test_get_config_path_default_filename(self):
        """Test get_config_path with default config.json filename."""
        config_path = ProjectPaths.get_config_path()
        
        assert isinstance(config_path, Path)
        assert config_path.name == "config.json"
        assert config_path.parent.name == "config"
    
    def test_get_config_path_custom_filename(self):
        """Test get_config_path with custom filename."""
        config_path = ProjectPaths.get_config_path("test_config.json")
        
        assert isinstance(config_path, Path)
        assert config_path.name == "test_config.json"
        assert config_path.parent.name == "config"
    
    def test_get_data_path_without_filename(self):
        """Test get_data_path returns data directory when no filename provided."""
        data_path = ProjectPaths.get_data_path()
        
        assert isinstance(data_path, Path)
        assert data_path.name == "data"
    
    def test_get_data_path_with_filename(self):
        """Test get_data_path with specific filename."""
        data_path = ProjectPaths.get_data_path("mva.csv")
        
        assert isinstance(data_path, Path)
        assert data_path.name == "mva.csv"
        assert data_path.parent.name == "data"
    
    def test_get_logs_path_without_filename(self):
        """Test get_logs_path returns logs directory when no filename provided."""
        logs_path = ProjectPaths.get_logs_path()
        
        assert isinstance(logs_path, Path)
        assert logs_path.name == "logs"
    
    def test_get_logs_path_with_filename(self):
        """Test get_logs_path with specific filename."""
        logs_path = ProjectPaths.get_logs_path("app.log")
        
        assert isinstance(logs_path, Path)
        assert logs_path.name == "app.log"
        assert logs_path.parent.name == "logs"
    
    def test_get_screenshots_path_without_filename(self):
        """Test get_screenshots_path returns screenshots directory when no filename provided."""
        screenshots_path = ProjectPaths.get_screenshots_path()
        
        assert isinstance(screenshots_path, Path)
        assert screenshots_path.name == "screenshots"
    
    def test_get_screenshots_path_with_filename(self):
        """Test get_screenshots_path with specific filename."""
        screenshots_path = ProjectPaths.get_screenshots_path("test_screenshot.png")
        
        assert isinstance(screenshots_path, Path)
        assert screenshots_path.name == "test_screenshot.png"
        assert screenshots_path.parent.name == "screenshots"
    
    def test_ensure_directory_exists_creates_directory(self):
        """Test that ensure_directory_exists creates directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "new_dir" / "nested_dir"
            
            # Directory shouldn't exist initially
            assert not test_path.exists()
            
            # ensure_directory_exists should create it
            result_path = ProjectPaths.ensure_directory_exists(test_path)
            
            assert test_path.exists()
            assert test_path.is_dir()
            assert result_path == test_path
    
    def test_ensure_directory_exists_with_existing_directory(self):
        """Test that ensure_directory_exists works with existing directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            
            # Directory already exists
            assert test_path.exists()
            
            # Should not raise error and return the path
            result_path = ProjectPaths.ensure_directory_exists(test_path)
            
            assert result_path == test_path
            assert test_path.is_dir()
    
    def test_ensure_directory_exists_accepts_string_path(self):
        """Test that ensure_directory_exists works with string paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path_str = os.path.join(temp_dir, "string_dir")
            
            # Directory shouldn't exist initially
            assert not os.path.exists(test_path_str)
            
            # ensure_directory_exists should create it
            result_path = ProjectPaths.ensure_directory_exists(test_path_str)
            
            assert os.path.exists(test_path_str)
            assert isinstance(result_path, Path)
            assert str(result_path) == os.path.abspath(test_path_str)


class TestBackwardCompatibilityFunctions:
    """Test backward compatibility convenience functions."""
    
    def setup_method(self):
        """Reset ProjectPaths cache before each test."""
        ProjectPaths._project_root = None
    
    def test_get_config_file_path_returns_string(self):
        """Test that get_config_file_path returns string path."""
        config_path = get_config_file_path()
        
        assert isinstance(config_path, str)
        assert config_path.endswith("config.json")
        assert "config" in config_path
    
    def test_get_config_file_path_custom_filename(self):
        """Test get_config_file_path with custom filename."""
        config_path = get_config_file_path("custom.json")
        
        assert isinstance(config_path, str)
        assert config_path.endswith("custom.json")
    
    def test_get_data_file_path_returns_string(self):
        """Test that get_data_file_path returns string path."""
        data_path = get_data_file_path("mva.csv")
        
        assert isinstance(data_path, str)
        assert data_path.endswith("mva.csv")
        assert "data" in data_path
    
    def test_get_project_root_path_returns_string(self):
        """Test that get_project_root_path returns string path."""
        root_path = get_project_root_path()
        
        assert isinstance(root_path, str)
        assert os.path.isabs(root_path)


class TestPathResolutionEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Reset ProjectPaths cache before each test."""
        ProjectPaths._project_root = None
    
    def test_paths_are_cross_platform_compatible(self):
        """Test that paths work on different operating systems."""
        config_path = ProjectPaths.get_config_path("test.json")
        data_path = ProjectPaths.get_data_path("test.csv")
        
        # Paths should use os-appropriate separators
        assert os.sep in str(config_path)
        assert os.sep in str(data_path)
        
        # Should be absolute paths
        assert config_path.is_absolute()
        assert data_path.is_absolute()
    
    def test_paths_resolve_consistently(self):
        """Test that multiple calls return equivalent paths."""
        config1 = ProjectPaths.get_config_path("test.json")
        config2 = ProjectPaths.get_config_path("test.json")
        
        assert config1 == config2
        assert str(config1) == str(config2)
    
    @patch('utils.project_paths.Path')
    def test_project_root_calculation_logic(self, mock_path):
        """Test the project root calculation logic."""
        # Mock the __file__ path to simulate being in utils/project_paths.py
        mock_file_path = Path("/fake/project/utils/project_paths.py")
        mock_path.return_value.parent.parent.resolve.return_value = Path("/fake/project")
        
        # Reset cache and call method
        ProjectPaths._project_root = None
        with patch('utils.project_paths.__file__', str(mock_file_path)):
            root = ProjectPaths.get_project_root()
        
        # Should have called the path resolution logic
        assert mock_path.return_value.parent.parent.resolve.called


class TestIntegrationWithExistingCode:
    """Integration tests to ensure ProjectPaths works with existing codebase."""
    
    def setup_method(self):
        """Reset ProjectPaths cache before each test."""
        ProjectPaths._project_root = None
    
    def test_config_path_matches_expected_location(self):
        """Test that config path points to actual config directory."""
        config_path = ProjectPaths.get_config_path()
        
        # Should point to existing config directory
        assert config_path.parent.exists()
        assert config_path.parent.name == "config"
    
    def test_data_path_matches_expected_location(self):
        """Test that data path points to actual data directory."""
        data_path = ProjectPaths.get_data_path()
        
        # Should point to existing data directory
        assert data_path.exists()
        assert data_path.name == "data"
    
    def test_mva_csv_path_resolution(self):
        """Test specific path resolution for mva.csv file."""
        mva_path = ProjectPaths.get_data_path("mva.csv")
        
        # Should resolve to the expected location
        assert mva_path.name == "mva.csv"
        assert mva_path.parent.name == "data"
        
        # File should exist (it's part of our test data)
        assert mva_path.exists()


if __name__ == "__main__":
    pytest.main([__file__])