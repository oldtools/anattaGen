import os
import json
import re
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QCoreApplication
from Python.ui.name_utils import normalize_name_for_matching
from Python.ui.steam_cache import STEAM_FILTERED_TXT, NORMALIZED_INDEX_CACHE # Only import constants, not functions

class SteamProcessor:
    def __init__(self, main_window, steam_cache_manager):
        self.main_window = main_window
        self.steam_cache_manager = steam_cache_manager

    def prompt_and_process_steam_json(self):
        """Prompt user to select and process Steam JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "Select Steam JSON file", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            # Backup existing cache files before processing
            self._backup_steam_cache_files()
            
            # Disable UI elements
            self._disable_ui_elements()
            self.main_window.statusBar().showMessage("Please be patient as the steam.json file is cached...", 0)
            
            # Process the file
            success = self.process_steam_json_file(file_path)
            
            # Re-enable UI elements
            self._enable_ui_elements()
            
            # Update status bar
            if success:
                self.main_window.statusBar().showMessage("Steam.json file indexing complete.", 5000)
            else:
                self.main_window.statusBar().showMessage("Steam.json file indexing failed.", 5000)

    def process_steam_json_file(self, input_json_path: str):
        """Process a Steam JSON file to extract title data"""
        if not os.path.exists(input_json_path):
            self.main_window.statusBar().showMessage(f"Steam JSON file not found: {input_json_path}", 5000)
            return False
        
        try:
            # Process the file
            self.main_window.statusBar().showMessage(f"Processing Steam JSON: {input_json_path}", 0)
            
            # Store the path for later reference
            self.main_window.steam_json_file_path = input_json_path
            
            # Load the JSON data
            with open(input_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Filter and extract title data
            self.main_window.steam_title_cache = {}
            
            # Handle different JSON structures
            apps_list = []
            
            if isinstance(data, dict):
                # Check if it's the standard Steam API format
                    if 'applist' in data and 'apps' in data['applist']:
                        # Check for the nested 'app' key
                        if isinstance(data['applist']['apps'], dict) and 'app' in data['applist']['apps']:
                            apps_list = data['applist']['apps']['app']
                            print(f"Found nested 'applist.apps.app' format with {len(apps_list)} apps")
                        else:
                            apps_list = data['applist']['apps']
                            print(f"Found standard 'applist.apps' format with {len(apps_list)} apps")
                    elif 'response' in data and 'apps' in data['response']:
                        apps_list = data['response']['apps']
                        print(f"Found 'response.apps' format with {len(apps_list)} apps")
                    else:
                        # Assume it's a direct mapping of app_id to app data
                        print("Assuming direct app_id to app_data mapping")
                        for app_id, app_data in data.items():
                            if isinstance(app_data, dict) and 'name' in app_data:
                                apps_list.append({
                                    'appid': app_id,
                                    'name': app_data['name'],
                                    'type': app_data.get('type', 'game')
                                })
                            elif isinstance(data, list):
                                # Direct list of apps
                                print(f"Found direct list of {len(data)} apps")
                                apps_list = data
            
            # Process the apps list
            print(f"Processing {len(apps_list)} apps")
            
            # Define exclusion terms and patterns
            exclusion_terms = [
                "soundtrack",
                "trailer",
                "dedicated server",
                "Closed Beta",
                "test app",
                "beta",
                "sdk",
                "editor",
                "tool",
                "dlc",
                "add-on",
                "plugins",
                "plug-ins",
                "Activation",
                "Artwork",
                "Wallpaper",
                "Preorder"
            ]
            
            regex_exclusion_patterns = [
                r"(?:\s[A-Za-z0-9]+)?\sDemo$",
                r"(?:\s[A-Za-z0-9]+)?\sAddons$",
                r"(?:\s[A-Za-z0-9]+)?\sBeta$",
                r"(?:\s[A-Za-z0-9]+)?\sTest$",
                r"(?:\s[A-Za-z0-9]+)?\sOST\s.*$",
                r"(?:\s[A-Za-z0-9]+)?\sServer$",
                r"(?:\s[A-Za-z0-9]+)?\sPatch$",
                r"(?:\s[A-Za-z0-9]+)?\sSet$"
            ]
            compiled_regex_exclusions = [re.compile(p, re.IGNORECASE) for p in regex_exclusion_patterns]
            
            # Filter out non-games, empty names, and duplicates
            filtered_apps = []
            seen_app_ids = set()  # Track seen app IDs to filter duplicates
            seen_app_names = {}   # Track seen app names to detect duplicates
            
            for app in apps_list:
                if not isinstance(app, dict):
                    print(f"Skipping app - Not a dictionary: {app}")
                    continue
                    
                app_id = app.get('appid')
                app_name = app.get('name')
                
                # Skip if missing required fields or empty name
                if not app_id or not app_name or not app_name.strip():
                    print(f"Skipping app '{app_name}' (ID: {app_id}) - Missing ID/Name or empty name.")
                    continue
                
                # Convert app_id to string
                app_id = str(app_id)
                
                # Skip duplicates by app_id
                if app_id in seen_app_ids:
                    print(f"Skipping duplicate app ID: {app_id} - '{app_name}'")
                    continue
                
                # Check for duplicate names (case insensitive)
                app_name_lower = app_name.lower()
                if app_name_lower in seen_app_names:
                    existing_id = seen_app_names[app_name_lower]
                    print(f"Found duplicate name: '{app_name}' - IDs: {existing_id} and {app_id}")
                    # Keep the one with the lower app_id (usually the original/main game)
                    if int(app_id) < int(existing_id):
                        # Replace the existing entry
                        print(f"Keeping app ID {app_id} for '{app_name}' (lower ID)")
                        # Remove the old entry from filtered_apps
                        filtered_apps = [app for app in filtered_apps if app[0] != existing_id]
                        # Update the seen_app_ids and seen_app_names
                        seen_app_ids.remove(existing_id)
                        seen_app_names[app_name_lower] = app_id
                    else:
                        # Skip this entry
                        print(f"Keeping existing app ID {existing_id} for '{app_name}' (lower ID)")
                        continue
                
                # Skip non-games if type is specified
                app_type = app.get('type', '').lower()
                if app_type and app_type not in ('game', 'dlc', 'application'):
                    print(f"Skipping app '{app_name}' (ID: {app_id}) - Type '{app_type}' is not game/dlc/application.")
                    continue
                    
                # Skip very short names or names with just common words
                if len(app_name) < 4:
                    print(f"Skipping app '{app_name}' (ID: {app_id}) - Name too short (length {len(app_name)}).")
                    continue
                
                # Skip if name contains exclusion terms
                if any(term in app_name_lower for term in exclusion_terms):
                    print(f"Skipping app '{app_name}' (ID: {app_id}) - Contains exclusion term.")
                    continue
                    
                # Skip if name matches regex exclusion patterns
                if any(rx.search(app_name) for rx in compiled_regex_exclusions):
                    print(f"Skipping app '{app_name}' (ID: {app_id}) - Matches regex exclusion pattern.")
                    continue
                    
                # Skip names that are just common words
                common_words = ["game", "the", "of", "and", "a", "an", "in", "on", "to", "for", "with", "by", "about"]
                words = app_name.lower().split()
                if all(word in common_words for word in words):
                    print(f"Skipping app with only common words: {app_name} (ID: {app_id})")
                    continue
                
                # Add to tracking sets
                seen_app_ids.add(app_id)
                seen_app_names[app_name_lower] = app_id
                
                # Add to filtered list
                filtered_apps.append((app_id, app_name))
                
                # Add to cache
                self.main_window.steam_title_cache[app_id] = app_name
            
            print(f"Filtered to {len(filtered_apps)} unique game apps (removed {len(apps_list) - len(filtered_apps)} entries)")
            
            # Get the app's root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(os.path.dirname(script_dir))
            
            # Save filtered data to a text file in the app root directory
            cache_file_path = os.path.join(app_root_dir, STEAM_FILTERED_TXT)
            print(f"Saving filtered Steam data to app root: {cache_file_path}")
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                for app_id, app_name in filtered_apps:
                    # Use tab as separator (less likely to appear in game names than pipe)
                    f.write(f"{app_id}\t{app_name}\n")
            
            if os.path.exists(cache_file_path) and os.path.getsize(cache_file_path) > 0:
                print(f"Successfully saved filtered Steam data to {cache_file_path} (size: {os.path.getsize(cache_file_path)} bytes)")
            else:
                print(f"Warning: Filtered Steam data file {cache_file_path} is empty or not created.")

            # Store the cache file path - make sure it's the .txt file
            self.main_window.filtered_steam_cache_file_path = cache_file_path
            print(f"Set filtered_steam_cache_file_path to: {cache_file_path}")
            
            # Create normalized index for better matching
            self.steam_cache_manager.create_normalized_steam_index()
            
            return True
            
        except Exception as e:
            import traceback
            print(f"Error processing Steam JSON: {e}")
            traceback.print_exc()
            self.main_window.statusBar().showMessage(f"Error processing Steam JSON: {str(e)}", 5000)
            return False

    def _disable_ui_elements(self):
        """Disable UI elements during processing"""
        # Disable main tabs
        for i in range(self.main_window.tabs.count()):
            tab = self.main_window.tabs.widget(i)
            tab.setEnabled(False)
        
        # Disable specific buttons
        if hasattr(self.main_window, 'process_steam_json_button'):
            self.main_window.process_steam_json_button.setEnabled(False)
        if hasattr(self.main_window, 'update_steam_json_button'):
            self.main_window.update_steam_json_button.setEnabled(False)
        
        # Process events to update UI
        QCoreApplication.processEvents()

    def _enable_ui_elements(self):
        """Re-enable UI elements after processing"""
        # Re-enable main tabs
        for i in range(self.main_window.tabs.count()):
            tab = self.main_window.tabs.widget(i)
            tab.setEnabled(True)
        
        # Re-enable specific buttons
        if hasattr(self.main_window, 'process_steam_json_button'):
            self.main_window.process_steam_json_button.setEnabled(True)
        if hasattr(self.main_window, 'update_steam_json_button'):
            self.main_window.update_steam_json_button.setEnabled(True)
        
        # Process events to update UI
        QCoreApplication.processEvents()

    def _backup_steam_cache_files(self):
        """Backup Steam cache files before processing"""
        import os
        import shutil
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(os.path.dirname(script_dir))
        
        # Get the cache file paths
        from Python.ui.steam_cache import STEAM_FILTERED_TXT, NORMALIZED_INDEX_CACHE
        filtered_cache_path = os.path.join(app_root_dir, STEAM_FILTERED_TXT)
        normalized_index_path = os.path.join(app_root_dir, NORMALIZED_INDEX_CACHE)
        
        # Backup filtered cache if it exists
        if os.path.exists(filtered_cache_path):
            backup_path = filtered_cache_path + ".old"
            try:
                # Remove old backup if it exists
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                
                # Create backup
                shutil.copy2(filtered_cache_path, backup_path)
                print(f"Backed up {STEAM_FILTERED_TXT} to {backup_path}")
            except Exception as e:
                print(f"Error backing up {STEAM_FILTERED_TXT}: {e}")
        
        # Backup normalized index if it exists
        if os.path.exists(normalized_index_path):
            backup_path = normalized_index_path + ".old"
            try:
                # Remove old backup if it exists
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                
                # Create backup
                shutil.copy2(normalized_index_path, backup_path)
                print(f"Backed up {NORMALIZED_INDEX_CACHE} to {backup_path}")
            except Exception as e:
                print(f"Error backing up {NORMALIZED_INDEX_CACHE}: {e}")
