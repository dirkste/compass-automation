import json
import os
from typing import Any


def _deep_merge(base: Any, override: Any) -> Any:
    """Deep-merge override into base (dicts only); override wins."""
    if not isinstance(base, dict) or not isinstance(override, dict):
        return override
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = _deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged

# Path to config.json in the same folder
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
CONFIG_LOCAL_PATH = os.path.join(os.path.dirname(__file__), "config.local.json")

# Load once at import (base + optional local override)
try:
    with open(CONFIG_PATH, "r") as f:
        _CONFIG = json.load(f)
except FileNotFoundError:
    raise RuntimeError(f"[CONFIG] Missing file: {CONFIG_PATH}")
except json.JSONDecodeError as e:
    raise RuntimeError(f"[CONFIG] Invalid JSON format in {CONFIG_PATH}: {e}")

if os.path.exists(CONFIG_LOCAL_PATH):
    try:
        with open(CONFIG_LOCAL_PATH, "r") as f:
            _local = json.load(f)
        _CONFIG = _deep_merge(_CONFIG, _local)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"[CONFIG] Invalid JSON format in {CONFIG_LOCAL_PATH}: {e}")


_ENV_OVERRIDES = {
    "username": "COMPASS_USERNAME",
    "password": "COMPASS_PASSWORD",
    "login_id": "COMPASS_LOGIN_ID",
}


def get_config(key: str, default: Any = None) -> Any:
    """
    Retrieve a config value by key, supporting dot notation for nested keys.

    Args:
        key: The key to look up in config.json (supports dot notation like "logging.level")
        default: Optional fallback if key is missing

    Returns:
        The value from config.json or the default if provided.
    """
    # Allow environment variable overrides for credentials.
    env_key = _ENV_OVERRIDES.get(key)
    if env_key:
        env_val = os.environ.get(env_key)
        if env_val is not None and str(env_val).strip() != "":
            return env_val

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
