"""
Handles propagation of files to profile folders
"""

import os
import shutil
import configparser
from PyQt6.QtCore import QCoreApplication

class FilePropagator:
    """Handles propagation of files to profile folders"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        self.max_file_size = 10 * 1024 * 1024  # 10 MB
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.app_directory = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    
    def propagate_files(self, game_data, profile_folder_path):
        """Propagate files to the profile folder"""
        if not profile_folder_path or not os.path.exists(profile_folder_path):
            print(f"Profile folder not found: {profile_folder_path}")
            return 0
        
        # Get the paths to propagate
        paths_to_propagate = self._get_paths_to_propagate()
        
        # Count propagated files
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
                
                # Replace variables in the path
                path = self._replace_variables(path, game_data)
                
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
        
        # Add controller mapper app
        if hasattr(self.main_window, 'controller_mapper_app_line_edit'):
            paths.append({
                'path': self.main_window.controller_mapper_app_line_edit.text(),
                'key': 'ControllerMapperApp'
            })
        
        # Add borderless windowing app
        if hasattr(self.main_window, 'borderless_app_line_edit'):
            paths.append({
                'path': self.main_window.borderless_app_line_edit.text(),
                'key': 'BorderlessWindowingApp'
            })
        
        # Add multi-monitor tool
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
        
        # Add pre-launch apps
        if hasattr(self.main_window, 'pre_launch_app_line_edits'):
            for i, le in enumerate(self.main_window.pre_launch_app_line_edits):
                paths.append({
                    'path': le.text(),
                    'key': f'PreLaunchApp{i+1}'
                })
        
        # Add post-launch apps
        if hasattr(self.main_window, 'post_launch_app_line_edits'):
            for i, le in enumerate(self.main_window.post_launch_app_line_edits):
                paths.append({
                    'path': le.text(),
                    'key': f'PostLaunchApp{i+1}'
                })
        
        # Add just after launch and just before exit apps
        if hasattr(self.main_window, 'after_launch_app_line_edit'):
            paths.append({
                'path': self.main_window.after_launch_app_line_edit.text(),
                'key': 'JustAfterLaunchApp'
            })
        
        if hasattr(self.main_window, 'before_exit_app_line_edit'):
            paths.append({
                'path': self.main_window.before_exit_app_line_edit.text(),
                'key': 'JustBeforeExitApp'
            })
        
        return paths
    
    def _replace_variables(self, path, game_data):
        """Replace variables in the path"""
        # Load variables from repos.set
        repos_set_path = os.path.join(self.app_directory, "Python", "repos.set")
        if os.path.exists(repos_set_path):
            repos_config = configparser.ConfigParser()
            repos_config.read(repos_set_path, encoding='utf-8')
            
            # Get SOURCEHOST and EXTRACTLOC from GLOBAL section
            if "GLOBAL" in repos_config:
                source_host = repos_config.get("GLOBAL", "SOURCEHOST", fallback="")
                extract_loc = repos_config.get("GLOBAL", "EXTRACTLOC", fallback="")
                
                # Replace variables
                path = path.replace("$SOURCEHOST", source_host)
                path = path.replace("$EXTRACTLOC", extract_loc)
        
        # Replace $app_directory with the actual app directory
        path = path.replace("$app_directory", self.app_directory)
        
        # Replace $ITEMNAME with the game name
        path = path.replace("$ITEMNAME", game_data['name_override'])
        
        return path



