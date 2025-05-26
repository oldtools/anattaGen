"""
Steam integration module - provides compatibility with Steam game library
This file now serves as an import point for backward compatibility
"""

# Import all functions from the new modules
from Python.ui.steam_cache import (
    load_filtered_steam_cache,
    reset_steam_caches,
    create_normalized_steam_index,
    save_normalized_steam_index,
    load_normalized_steam_index,
    STEAM_FILTERED_TXT,
    NORMALIZED_INDEX_CACHE
)

from Python.ui.steam_processor import (
    prompt_and_process_steam_json,
    process_steam_json_file
)

from Python.ui.steam_utils import (
    locate_and_exclude_manager_config,
    debug_steam_cache,
    debug_steam_cache_loading
)

# For backward compatibility, re-export all the imported functions
__all__ = [
    'load_filtered_steam_cache',
    'reset_steam_caches',
    'create_normalized_steam_index',
    'save_normalized_steam_index',
    'load_normalized_steam_index',
    'prompt_and_process_steam_json',
    'process_steam_json_file',
    'locate_and_exclude_manager_config',
    'debug_steam_cache',
    'debug_steam_cache_loading',
    'STEAM_FILTERED_TXT',
    'NORMALIZED_INDEX_CACHE'
]