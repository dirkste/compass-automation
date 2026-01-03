"""
Central path management utility for the compass-automation project.

This module provides a single source of truth for all project paths,
eliminating hardcoded paths scattered throughout the codebase.
"""
import os
from pathlib import Path
from typing import Union


class ProjectPaths:
    """Central utility for managing project file paths."""
    
    _project_root = None
    
    @classmethod
    def get_project_root(cls) -> Path:
        """
        Get the absolute path to the project root directory.
        
        Returns:
            Path: Absolute path to project root (directory containing this file's parent's parent)
        """
        if cls._project_root is None:
            # This file is in src/compass_automation/utils/, so project root is three levels up
            cls._project_root = Path(__file__).parent.parent.parent.parent.resolve()
        return cls._project_root
    
    @classmethod
    def get_config_path(cls, filename: str = "config.json") -> Path:
        """
        Get path to a configuration file.
        
        Args:
            filename: Name of the config file (default: config.json)
            
        Returns:
            Path: Absolute path to the config file
        """
        return cls.get_project_root() / "src" / "compass_automation" / "config" / filename
    
    @classmethod
    def get_data_path(cls, filename: str = None) -> Path:
        """
        Get path to a data file or the data directory.
        
        Args:
            filename: Name of the data file (optional)
            
        Returns:
            Path: Absolute path to data file or data directory if filename is None
        """
        data_dir = cls.get_project_root() / "data"
        if filename:
            return data_dir / filename
        return data_dir
    
    @classmethod
    def get_logs_path(cls, filename: str = None) -> Path:
        """
        Get path to a log file or logs directory.
        
        Args:
            filename: Name of the log file (optional)
            
        Returns:
            Path: Absolute path to log file or logs directory if filename is None
        """
        logs_dir = cls.get_project_root() / "logs"
        if filename:
            return logs_dir / filename
        return logs_dir
    
    @classmethod
    def get_screenshots_path(cls, filename: str = None) -> Path:
        """
        Get path to a screenshot file or screenshots directory.
        
        Args:
            filename: Name of the screenshot file (optional)
            
        Returns:
            Path: Absolute path to screenshot file or screenshots directory if filename is None
        """
        screenshots_dir = cls.get_project_root() / "screenshots"
        if filename:
            return screenshots_dir / filename
        return screenshots_dir
    
    @classmethod
    def ensure_directory_exists(cls, path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path to ensure exists
            
        Returns:
            Path: The ensured directory path
        """
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path


# Convenience functions for backward compatibility and ease of use
def get_config_file_path(filename: str = "config.json") -> str:
    """Get config file path as string (backward compatible)."""
    return str(ProjectPaths.get_config_path(filename))


def get_data_file_path(filename: str) -> str:
    """Get data file path as string (backward compatible)."""
    return str(ProjectPaths.get_data_path(filename))


def get_project_root_path() -> str:
    """Get project root path as string (backward compatible)."""
    return str(ProjectPaths.get_project_root())