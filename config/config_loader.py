import json
import os
from typing import Any

# Path to config.json in the same folder
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# Load once at import
try:
    with open(CONFIG_PATH, "r") as f:
        _CONFIG = json.load(f)
except FileNotFoundError:
    raise RuntimeError(f"[CONFIG] Missing file: {CONFIG_PATH}")
except json.JSONDecodeError as e:
    raise RuntimeError(f"[CONFIG] Invalid JSON format in {CONFIG_PATH}: {e}")


def get_config(key: str, default: Any = None) -> Any:
    """
    Retrieve a config value by key, supporting dot notation for nested keys.

    Args:
        key: The key to look up in config.json (supports dot notation like "logging.level")
        default: Optional fallback if key is missing

    Returns:
        The value from config.json or the default if provided.
    """
    # Handle nested keys with dot notation
    if '.' in key:
        keys = key.split('.')
        value = _CONFIG
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            if default is None:
                raise KeyError(f"[CONFIG] Missing nested key: '{key}' in {CONFIG_PATH}")
            return default
    
    # Handle simple keys
    if key not in _CONFIG and default is None:
        raise KeyError(f"[CONFIG] Missing key: '{key}' in {CONFIG_PATH}")
    return _CONFIG.get(key, default)

DEFAULT_TIMEOUT = _CONFIG.get("delay_seconds", 8)
