import os
import json
from Python.ui.name_utils import normalize_name_for_matching

# Constants
STEAM_FILTERED_TXT = "steam_filtered.txt"
NORMALIZED_INDEX_CACHE = "steam_normalized_index.json"

class SteamCacheManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def fix_steam_cache_file_path(self):
        """Check and fix the steam cache file path if needed"""
        print("Checking steam cache file path...")
        
        # Check if the attribute exists
        if not hasattr(self.main_window, 'filtered_steam_cache_file_path'):
            print("filtered_steam_cache_file_path attribute does not exist")
            return False
        
        # Check if it's set
        if not self.main_window.filtered_steam_cache_file_path:
            print("filtered_steam_cache_file_path is not set")
            return False
        
        # Check if it's pointing to a .json file
        if self.main_window.filtered_steam_cache_file_path.endswith('.json'):
            # Try to find the .txt version
            txt_path = self.main_window.filtered_steam_cache_file_path.replace('.json', '.txt')
            if os.path.exists(txt_path):
                print(f"Found .txt version at {txt_path}, updating path")
                self.main_window.filtered_steam_cache_file_path = txt_path
                return True
            else:
                # Look in the same directory
                dir_path = os.path.dirname(self.main_window.filtered_steam_cache_file_path)
                txt_file = os.path.join(dir_path, STEAM_FILTERED_TXT)
                if os.path.exists(txt_file):
                    print(f"Found {STEAM_FILTERED_TXT} in same directory, updating path")
                    self.main_window.filtered_steam_cache_file_path = txt_file
                    return True
                else:
                    print(f"Could not find a .txt version of the cache file")
                    return False
        
        # Check if the file exists
        if not os.path.exists(self.main_window.filtered_steam_cache_file_path):
            print(f"Cache file not found at {self.main_window.filtered_steam_cache_file_path}")
            
            # Try to find it in the same directory
            dir_path = os.path.dirname(self.main_window.filtered_steam_cache_file_path)
            txt_file = os.path.join(dir_path, STEAM_FILTERED_TXT)
            if os.path.exists(txt_file):
                print(f"Found {STEAM_FILTERED_TXT} in same directory, updating path")
                self.main_window.filtered_steam_cache_file_path = txt_file
                return True
            else:
                # Try to find it in the script directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                txt_file = os.path.join(script_dir, STEAM_FILTERED_TXT)
                if os.path.exists(txt_file):
                    print(f"Found {STEAM_FILTERED_TXT} in script directory, updating path")
                    self.main_window.filtered_steam_cache_file_path = txt_file
                    return True
                else:
                    print(f"Could not find {STEAM_FILTERED_TXT} anywhere")
                    return False
        
        return True

    def load_filtered_steam_cache(self):
        """Load the filtered Steam cache file if it exists"""
        # Clear existing caches first - do this unconditionally
        print("Clearing existing Steam caches")
        self.main_window.steam_title_cache = {}
        self.main_window.normalized_steam_match_index = {}
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(os.path.dirname(script_dir))
        
        # Check if the file exists in the app root
        steam_filtered_path = os.path.join(app_root_dir, STEAM_FILTERED_TXT)
        
        if not os.path.exists(steam_filtered_path):
            print(f"Filtered Steam cache file not found at app root: {steam_filtered_path}")
            return False
        
        # Set the path for future reference
        self.main_window.filtered_steam_cache_file_path = steam_filtered_path
        
        # First try to load the normalized index cache if it exists
        normalized_index_loaded = self.load_normalized_steam_index()
        
        # Always load the filtered cache to ensure we have the complete title cache
        print(f"Loading filtered Steam cache from: {steam_filtered_path}")
        try:
            with open(steam_filtered_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split('\t')  # Use tab as separator
                        if len(parts) >= 2:
                            app_id = parts[0]
                            title = parts[1]
                            self.main_window.steam_title_cache[app_id] = title
        
            print(f"Loaded {len(self.main_window.steam_title_cache)} Steam titles")
        
            # If normalized index wasn't loaded or is incomplete, create it
            if not normalized_index_loaded or len(self.main_window.normalized_steam_match_index) < len(self.main_window.steam_title_cache) * 0.9:
                print("Normalized index not loaded or incomplete, creating new one")
                self.create_normalized_steam_index()
        
            return True
        except Exception as e:
            print(f"Error loading filtered Steam cache: {e}")
            return False

    def create_normalized_steam_index(self):
        """Create normalized index for better matching"""
        print("Creating normalized index for matching")
        
        self.main_window.normalized_steam_match_index = {}
        
        # Debug counters
        total_titles = len(self.main_window.steam_title_cache)
        skipped_count = 0
        added_count = 0
        
        for app_id, title in self.main_window.steam_title_cache.items():
            # Skip empty titles
            if not title:
                skipped_count += 1
                print(f"Skipping empty title for app ID: {app_id}")
                continue
            
            # Normalize the title (do not use stemmer for Steam names to prevent improper culling)
            normalized = normalize_name_for_matching(title, None)
            
            # Special handling for short titles (4 chars or less)
            # These are often acronyms or unique names that should be preserved
            if len(title) <= 4:
                print(f"Special handling for short title: '{title}' -> '{normalized}'")
                # For very short titles, we'll keep them even if they'd normally be filtered
                self.main_window.normalized_steam_match_index[normalized] = {"id": app_id, "name": title}
                added_count += 1
                continue
                
            # Skip empty normalized names
            if not normalized:
                skipped_count += 1
                print(f"Skipping empty normalized name: '{title}' -> '{normalized}'")
                continue
                
            # Skip if normalized name is too generic (single word that's too common)
            generic_words = ["game", "about", "the", "and", "for", "with"]
            if normalized in generic_words and len(normalized.split()) == 1:
                skipped_count += 1
                print(f"Skipping generic normalized name: '{title}' -> '{normalized}'")
                continue
                
            # Add to normalized index
            self.main_window.normalized_steam_match_index[normalized] = {"id": app_id, "name": title}
            added_count += 1
        
        print(f"Created normalized index with {len(self.main_window.normalized_steam_match_index)} entries")
        print(f"Total titles: {total_titles}, Added: {added_count}, Skipped: {skipped_count}")
        
        # Save the normalized index to a cache file
        self.save_normalized_steam_index()
        
        return True

    def save_normalized_steam_index(self):
        """Save the normalized index to a cache file for faster loading"""
        if not hasattr(self.main_window, 'normalized_steam_match_index') or not self.main_window.normalized_steam_match_index:
            print("No normalized index to save")
            return False
        
        try:
            # Get the app's root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(os.path.dirname(script_dir))
            
            # Save to app root directory
            cache_file = os.path.join(app_root_dir, NORMALIZED_INDEX_CACHE)
            
            # Save the index
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.main_window.normalized_steam_match_index, f, ensure_ascii=False, indent=2)
            
            print(f"Saved normalized index to {cache_file}")
            return True
        except Exception as e:
            print(f"Error saving normalized index: {e}")
            return False

    def load_normalized_steam_index(self):
        """Load the normalized index from a cache file if it exists"""
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(os.path.dirname(script_dir))
        
        # Check if the file exists in the app root
        cache_file = os.path.join(app_root_dir, NORMALIZED_INDEX_CACHE)
        
        if not os.path.exists(cache_file):
            print(f"Normalized index cache file not found at app root: {cache_file}")
            return False
        
        try:
            # Load the index
            print(f"Loading normalized index from: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                self.main_window.normalized_steam_match_index = json.load(f)
            
            print(f"Loaded normalized index with {len(self.main_window.normalized_steam_match_index)} entries")
            
            # Debug: Print a few sample entries
            sample_count = min(5, len(self.main_window.normalized_steam_match_index))
            print(f"Sample entries from normalized index:")
            for i, (norm_name, data) in enumerate(list(self.main_window.normalized_steam_match_index.items())[:sample_count]):
                print(f"  {i+1}. '{norm_name}' -> {data['name']} (ID: {data['id']})")
            
            return True
        except Exception as e:
            print(f"Error loading normalized index: {e}")
            return False

    def reset_steam_caches(self):
        """Completely reset all Steam-related caches and data"""
        print("Resetting all Steam-related caches and data")
        
        # Clear the main caches
        self.main_window.steam_title_cache = {}
        self.main_window.normalized_steam_match_index = {}
        
        # Clear any other related attributes
        if hasattr(self.main_window, 'filtered_steam_cache_file_path'):
            self.main_window.filtered_steam_cache_file_path = None
        
        if hasattr(self.main_window, 'steam_json_file_path'):
            self.main_window.steam_json_file_path = None
        
        # Clear any other potential caches
        for attr_name in dir(self.main_window):
            if attr_name.startswith('steam_') and attr_name not in ('steam_title_cache', 'steam_json_file_path'):
                setattr(self.main_window, attr_name, None)
        
        print("Steam caches reset complete")
        return True
