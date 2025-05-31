"""
Manages creation and updating of game profile folders
"""

import os
import shutil
import configparser
from PyQt6.QtCore import QCoreApplication

class ProfileManager:
    """Handles creation and updating of game profile folders"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
    
    def get_profile_folder_path(self, game_data):
        """Get the path to the profile folder for a game"""
        # Get the profiles directory
        profiles_dir = self.main_window.profiles_dir_edit.text()
        if not profiles_dir or not os.path.isdir(profiles_dir):
            print(f"Profiles directory not found: {profiles_dir}")
            return None
        
        # Get the game name from name_override
        game_name = game_data['name_override']
        if not game_name:
            print(f"Game name not found for {game_data['executable']}")
            return None
        
        # Create the profile folder path
        return os.path.join(profiles_dir, game_name)
    
    def create_profile_folder(self, game_data):
        """Create a profile folder for the game"""
        # Get the profile folder path
        profile_folder_path = self.get_profile_folder_path(game_data)
        if not profile_folder_path:
            return {'created': False, 'updated': False}
        
        # Check if the profile folder already exists
        folder_exists = os.path.exists(profile_folder_path)
        
        # Create the profile folder if it doesn't exist
        try:
            os.makedirs(profile_folder_path, exist_ok=True)
            print(f"{'Created' if not folder_exists else 'Using existing'} profile folder: {profile_folder_path}")
            return {'created': not folder_exists, 'updated': folder_exists}
        except Exception as e:
            print(f"Error creating profile folder: {e}")
            return {'created': False, 'updated': False}
    
    def propagate_assets(self, game_data, profile_folder_path):
        """Propagate assets to the profile folder"""
        if not profile_folder_path or not os.path.exists(profile_folder_path):
            print(f"Profile folder not found: {profile_folder_path}")
            return 0
        
        # Get the paths to propagate
        paths_to_propagate = self._get_paths_to_propagate()
        
        # Count propagated assets
        propagated_count = 0
        
        # Process each path
        for path_info in paths_to_propagate:
            path = path_info['path']
            key = path_info['key']
            
            # Skip empty paths
            if not path:
                continue
            
            # Check if the path is marked with '>'
            if path.startswith('>'):
                # Remove the '>' marker
                path = path[1:]
                
                # Check if the file exists
                if not os.path.exists(path):
                    print(f"File not found: {path}")
                    continue
                
                # Get the destination path
                dest_path = os.path.join(profile_folder_path, os.path.basename(path))
                
                # Copy the file
                try:
                    if os.path.isfile(path):
                        shutil.copy2(path, dest_path)
                        propagated_count += 1
                    elif os.path.isdir(path):
                        # Copy the directory recursively
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(path, dest_path)
                        propagated_count += 1
                except Exception as e:
                    print(f"Error copying file: {e}")
        
        return propagated_count
    
    def _get_paths_to_propagate(self):
        """Get the paths to propagate from the UI"""
        paths = []
        
        # Add paths from the UI
        if hasattr(self.main_window, 'controller_mapper_app_line_edit'):
            paths.append({
                'path': self.main_window.controller_mapper_app_line_edit.text(),
                'key': 'ControllerMapperApp'
            })
        
        if hasattr(self.main_window, 'borderless_app_line_edit'):
            paths.append({
                'path': self.main_window.borderless_app_line_edit.text(),
                'key': 'BorderlessWindowingApp'
            })
        
        if hasattr(self.main_window, 'multimonitor_app_line_edit'):
            paths.append({
                'path': self.main_window.multimonitor_app_line_edit.text(),
                'key': 'MultiMonitorTool'
            })
        
        # Add player profiles
        if hasattr(self.main_window, 'p1_profile_edit'):
            paths.append({
                'path': self.main_window.p1_profile_edit.text(),
                'key': 'Player1Profile'
            })
        
        if hasattr(self.main_window, 'p2_profile_edit'):
            paths.append({
                'path': self.main_window.p2_profile_edit.text(),
                'key': 'Player2Profile'
            })
        
        # Add monitor configs
        if hasattr(self.main_window, 'multimonitor_gaming_config_edit'):
            paths.append({
                'path': self.main_window.multimonitor_gaming_config_edit.text(),
                'key': 'MultiMonitorGamingConfig'
            })
        
        if hasattr(self.main_window, 'multimonitor_media_config_edit'):
            paths.append({
                'path': self.main_window.multimonitor_media_config_edit.text(),
                'key': 'MultiMonitorMediaConfig'
            })
        
        # Add pre-launch and post-launch apps
        for i in range(1, 4):
            if hasattr(self.main_window, f'pre_launch_app{i}_edit'):
                paths.append({
                    'path': getattr(self.main_window, f'pre_launch_app{i}_edit').text(),
                    'key': f'PreLaunchApp{i}'
                })
            
            if hasattr(self.main_window, f'post_launch_app{i}_edit'):
                paths.append({
                    'path': getattr(self.main_window, f'post_launch_app{i}_edit').text(),
                    'key': f'PostLaunchApp{i}'
                })
        
        # Add just after launch and just before exit apps
        if hasattr(self.main_window, 'just_after_launch_app_edit'):
            paths.append({
                'path': self.main_window.just_after_launch_app_edit.text(),
                'key': 'JustAfterLaunchApp'
            })
        
        if hasattr(self.main_window, 'just_before_exit_app_edit'):
            paths.append({
                'path': self.main_window.just_before_exit_app_edit.text(),
                'key': 'JustBeforeExitApp'
            })
        
        return paths


