"""
Steam integration module - provides compatibility with Steam game library
This file now serves as an import point for backward compatibility
"""

# Import all functions from the new modules
from Python.ui.steam_cache import (
    SteamCacheManager,
    STEAM_FILTERED_TXT,
    NORMALIZED_INDEX_CACHE
)

from Python.ui.steam_processor import (
    SteamProcessor
)

from Python.ui.steam_utils import (
    locate_and_exclude_manager_config,
    debug_steam_cache,
    debug_steam_cache_loading
)

# For backward compatibility, define wrapper functions
def load_filtered_steam_cache(main_window):
    """Wrapper for SteamCacheManager.load_filtered_steam_cache"""
    if hasattr(main_window, 'steam_cache_manager'):
        return main_window.steam_cache_manager.load_filtered_steam_cache()
    else:
        # Create a temporary manager if needed
        manager = SteamCacheManager(main_window)
        return manager.load_filtered_steam_cache()

def reset_steam_caches(main_window):
    """Wrapper for SteamCacheManager.reset_steam_caches"""
    if hasattr(main_window, 'steam_cache_manager'):
        return main_window.steam_cache_manager.reset_steam_caches()
    else:
        # Create a temporary manager if needed
        manager = SteamCacheManager(main_window)
        return manager.reset_steam_caches()

def create_normalized_steam_index(main_window):
    """Wrapper for SteamCacheManager.create_normalized_steam_index"""
    if hasattr(main_window, 'steam_cache_manager'):
        return main_window.steam_cache_manager.create_normalized_steam_index()
    else:
        # Create a temporary manager if needed
        manager = SteamCacheManager(main_window)
        return manager.create_normalized_steam_index()

def save_normalized_steam_index(main_window):
    """Wrapper for SteamCacheManager.save_normalized_steam_index"""
    if hasattr(main_window, 'steam_cache_manager'):
        return main_window.steam_cache_manager.save_normalized_steam_index()
    else:
        # Create a temporary manager if needed
        manager = SteamCacheManager(main_window)
        return manager.save_normalized_steam_index()

def load_normalized_steam_index(main_window):
    """Wrapper for SteamCacheManager.load_normalized_steam_index"""
    if hasattr(main_window, 'steam_cache_manager'):
        return main_window.steam_cache_manager.load_normalized_steam_index()
    else:
        # Create a temporary manager if needed
        manager = SteamCacheManager(main_window)
        return manager.load_normalized_steam_index()

def prompt_and_process_steam_json(main_window):
    """Wrapper for SteamProcessor.prompt_and_process_steam_json"""
    if not hasattr(main_window, 'steam_processor'):
        # Create a processor if needed
        if hasattr(main_window, 'steam_cache_manager'):
            main_window.steam_processor = SteamProcessor(main_window, main_window.steam_cache_manager)
        else:
            # Create both manager and processor
            main_window.steam_cache_manager = SteamCacheManager(main_window)
            main_window.steam_processor = SteamProcessor(main_window, main_window.steam_cache_manager)
    
    return main_window.steam_processor.prompt_and_process_steam_json()

def process_steam_json_file(main_window, input_json_path):
    """Wrapper for SteamProcessor.process_steam_json_file"""
    if not hasattr(main_window, 'steam_processor'):
        # Create a processor if needed
        if hasattr(main_window, 'steam_cache_manager'):
            main_window.steam_processor = SteamProcessor(main_window, main_window.steam_cache_manager)
        else:
            # Create both manager and processor
            main_window.steam_cache_manager = SteamCacheManager(main_window)
            main_window.steam_processor = SteamProcessor(main_window, main_window.steam_cache_manager)
    
    return main_window.steam_processor.process_steam_json_file(input_json_path)

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
