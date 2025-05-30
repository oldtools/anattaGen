"""
Manages joystick mapping profiles for games
"""

import os
import shutil
import configparser
from PyQt6.QtCore import QCoreApplication

class JoystickProfileManager:
    """Handles joystick mapping profiles for games"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        self.max_file_size = 181 * 1024  # 181 KB
    
    def process_joystick_profiles(self, game_data, create_profile_folders, overwrite_existing=False):
        """Process joystick profiles for a game"""
        # Get the profiles directory
        profiles_dir = self.main_window.profiles_dir_edit.text() if hasattr(self.main_window, 'profiles_dir_edit') else None
        
        # Try to get profiles directory from config if not available in UI
        if not profiles_dir or not os.path.isdir(profiles_dir):
            try:
                import configparser
                config = configparser.ConfigParser()
                script_dir = os.path.dirname(os.path.abspath(__file__))
                app_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
                config_path = os.path.join(app_root_dir, "config.ini")
                if os.path.exists(config_path):
                    config.read(config_path, encoding='utf-8')
                    profiles_dir = config.get("Element Locations", "profiles_directory", fallback=None)
                    if profiles_dir and os.path.isdir(profiles_dir):
                        print(f"Using profiles directory from config: {profiles_dir}")
                        # Set it in the UI if possible
                        if hasattr(self.main_window, 'profiles_dir_edit'):
                            self.main_window.profiles_dir_edit.setText(profiles_dir)
            except Exception as e:
                print(f"Error getting profiles directory from config: {e}")
        
        if not profiles_dir or not os.path.isdir(profiles_dir):
            print(f"Profiles directory not found or invalid: '{profiles_dir}'")
            return {'created': 0, 'updated': 0}
        
        # Get the game name from name_override
        game_name = game_data['name_override']
        if not game_name:
            print(f"Game name not found for {game_data['executable']}")
            return {'created': 0, 'updated': 0}
        
        # Create the profile folder path
        profile_folder_path = os.path.join(profiles_dir, game_name)
        
        # Check if the profile folder exists
        if not os.path.exists(profile_folder_path) and not create_profile_folders:
            print(f"Profile folder does not exist and create_profile_folders is False: {profile_folder_path}")
            return {'created': 0, 'updated': 0}
        
        # Make sure the profile folder exists
        os.makedirs(profile_folder_path, exist_ok=True)
        
        # Get the config file path
        config_file_path = os.path.join(profile_folder_path, "Game.ini")
        
        # Check if the config file exists
        config_exists = os.path.exists(config_file_path)
        
        # Create the config parser
        config = configparser.ConfigParser()
        config.optionxform = str  # Preserve case for keys
        
        # If the config file exists, load it
        if config_exists:
            try:
                config.read(config_file_path, encoding='utf-8')
            except Exception as e:
                print(f"Error reading config file: {e}")
                # Create a new config
                config = configparser.ConfigParser()
                config.optionxform = str  # Preserve case for keys
        
        # Ensure the Paths section exists
        if 'Paths' not in config:
            config['Paths'] = {}
        
        # Get the profiles to process
        profiles = self._get_profiles_to_process()
        
        # Process each profile
        results = {'created': 0, 'updated': 0}
        
        for profile in profiles:
            profile_key = profile['key']
            profile_path = profile['path']
            
            # Skip empty paths
            if not profile_path:
                continue
            
            # Check if the profile is marked with '>'
            if profile_path.startswith('>'):
                # Remove the '>' marker
                profile_path = profile_path[1:]
                
                # Update the config with the absolute path
                if profile_path:
                    config['Paths'][profile_key] = profile_path
                    results['updated'] += 1
                else:
                    # If the path is empty, remove the key
                    if profile_key in config['Paths']:
                        del config['Paths'][profile_key]
            
            # Check if the profile is marked with '<'
            elif profile_path.startswith('<'):
                # Remove the '<' marker
                profile_path = profile_path[1:]
                
                # Update the config with the absolute path
                if profile_path:
                    config['Paths'][profile_key] = profile_path
                    results['updated'] += 1
                else:
                    # If the path is empty, remove the key
                    if profile_key in config['Paths']:
                        del config['Paths'][profile_key]
            
            # Otherwise, only update if the key doesn't exist or overwrite_existing is True
            elif overwrite_existing or profile_key not in config['Paths'] or not config['Paths'][profile_key]:
                config['Paths'][profile_key] = profile_path
                if profile_key in config['Paths']:
                    results['updated'] += 1
                else:
                    results['created'] += 1
        
        # Write the config file
        try:
            with open(config_file_path, 'w', encoding='utf-8') as f:
                config.write(f)
        except Exception as e:
            print(f"Error writing config file: {e}")
        
        return results
    
    def _get_profiles_to_process(self):
        """Get the profiles to process from the UI"""
        profiles = []
        
        # Add profiles from the UI
        if hasattr(self.main_window, 'p1_profile_edit'):
            profiles.append({
                'path': self.main_window.p1_profile_edit.text(),
                'key': 'Player1Profile'
            })
        
        if hasattr(self.main_window, 'p2_profile_edit'):
            profiles.append({
                'path': self.main_window.p2_profile_edit.text(),
                'key': 'Player2Profile'
            })
        
        if hasattr(self.main_window, 'mediacenter_profile_edit'):
            profiles.append({
                'path': self.main_window.mediacenter_profile_edit.text(),
                'key': 'MediaCenterProfile'
            })
        
        return profiles
    
    def _get_destination_path(self, source_path, profile_folder_path, diversion_dir, game_name):
        """Get the destination path for a joystick profile"""
        # Get the file name
        file_name = os.path.basename(source_path)
        
        # If there's a diversion directory, use it
        if diversion_dir:
            # Replace variables in the diversion directory
            diversion_dir = diversion_dir.replace('$OVR', game_name)
            diversion_dir = diversion_dir.replace('$EXT', os.path.splitext(file_name)[1][1:])
            
            # Create the full destination path
            dest_dir = os.path.join(profile_folder_path, diversion_dir)
            
            # If the diversion directory ends with a file extension, it's a full path
            if os.path.splitext(diversion_dir)[1]:
                return dest_dir
            else:
                # Otherwise, append the original filename
                return os.path.join(dest_dir, file_name)
        
        # Otherwise, use the profile folder
        return os.path.join(profile_folder_path, file_name)

