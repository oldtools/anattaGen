"""
Manages the creation of shortcuts for games and launchers
"""

import os
import sys
import subprocess
from pathlib import Path
import win32com.client

class ShortcutManager:
    """Manages the creation of shortcuts for games and launchers"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        
        # Get the launcher executable path
        self.launcher_exe_path = self._get_launcher_exe_path()
    
    def _get_launcher_exe_path(self):
        """Get the path to the launcher executable"""
        # First try to find launcher.exe in the same directory as the script
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        launcher_exe = os.path.join(script_dir, "launcher.exe")
        
        if os.path.exists(launcher_exe):
            print(f"Found launcher.exe in script directory: {launcher_exe}")
            return launcher_exe
        
        # If not found, try to find it in the bin directory
        bin_dir = os.path.join(script_dir, "bin")
        launcher_exe = os.path.join(bin_dir, "launcher.exe")
        
        if os.path.exists(launcher_exe):
            print(f"Found launcher.exe in bin directory: {launcher_exe}")
            return launcher_exe
        
        # If still not found, try to find it in the parent directory
        parent_dir = os.path.dirname(script_dir)
        launcher_exe = os.path.join(parent_dir, "launcher.exe")
        
        if os.path.exists(launcher_exe):
            print(f"Found launcher.exe in parent directory: {launcher_exe}")
            return launcher_exe
        
        # If still not found, use a relative path and hope for the best
        return os.path.join("..", "launcher.exe")
    
    def create_game_shortcut(self, game_data, profile_folder_path):
        """Create a shortcut to the game in the profile folder"""
        # Get the game name from name_override
        game_name = game_data['name_override']
        if not game_name:
            print(f"Game name not found for {game_data['executable']}")
            return False
        
        # Create the shortcut path
        shortcut_path = os.path.join(profile_folder_path, f"{game_name}.lnk")
        
        # Get the game executable path
        game_exe_path = os.path.join(game_data['directory'], game_data['executable'])
        if not os.path.exists(game_exe_path):
            print(f"Game executable not found: {game_exe_path}")
            return False
        
        # Create the shortcut
        if sys.platform == 'win32':
            try:
                return self._create_com_shortcut(
                    shortcut_path,
                    game_exe_path,
                    game_data['directory'],
                    game_data.get('arguments', ''),
                    game_exe_path,
                    0
                )
            except Exception as e:
                print(f"Error creating game shortcut: {e}")
                return False
        else:
            print("Shortcut creation not supported on this platform")
            return False
    
    def create_launcher_shortcut(self, game_data, profile_folder_path, launchers_dir):
        """Create a shortcut to the launcher in the launchers directory"""
        # Get the game name from name_override
        game_name = game_data['name_override']
        if not game_name:
            print(f"Game name not found for {game_data['executable']}")
            return False
        
        # Create the launcher shortcut path
        launcher_shortcut_path = os.path.join(launchers_dir, f"{game_name}.lnk")
        
        # Get the game executable path for icon extraction
        game_exe_path = os.path.join(game_data['directory'], game_data['executable'])
        if not os.path.exists(game_exe_path):
            print(f"Game executable not found: {game_exe_path}")
            return False
        
        # Create the profile shortcut path (this will be the argument for launcher.exe)
        profile_shortcut_path = os.path.join(profile_folder_path, f"{game_name}.lnk")
        
        # Make sure the launcher executable path is absolute
        launcher_exe_path = self.launcher_exe_path
        if not os.path.isabs(launcher_exe_path):
            # Convert relative path to absolute
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            launcher_exe_path = os.path.abspath(os.path.join(script_dir, launcher_exe_path))
            print(f"Using absolute launcher path: {launcher_exe_path}")
        
        # Create the shortcut
        if sys.platform == 'win32':
            try:
                # Create a shortcut to launcher.exe with the profile shortcut as argument
                result = self._create_com_shortcut(
                    launcher_shortcut_path,
                    launcher_exe_path,         # Target is launcher.exe (absolute path)
                    os.path.dirname(profile_shortcut_path),  # Working directory is profile directory
                    f'"{profile_shortcut_path}"',  # Argument is the profile shortcut (with quotes)
                    game_exe_path,             # Icon from the game executable
                    0                          # Icon index
                )
                
                if result:
                    print(f"Created launcher shortcut: {launcher_shortcut_path}")
                    print(f"  Target: {launcher_exe_path}")
                    print(f"  Working directory: {os.path.dirname(profile_shortcut_path)}")
                    print(f"  Arguments: {profile_shortcut_path}")
                return result
            except Exception as e:
                print(f"Error creating launcher shortcut: {e}")
                return False
        else:
            print("Shortcut creation not supported on this platform")
            return False
    
    def _create_com_shortcut(self, shortcut_path, target_path, working_dir, arguments, icon_path, icon_index):
        """Create a Windows shortcut (.lnk file) using COM objects"""
        try:
            # Make sure the directory exists
            os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)
            
            # Create a shell object
            shell = win32com.client.Dispatch("WScript.Shell")
            
            # Create the shortcut
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = working_dir
            shortcut.Arguments = arguments
            shortcut.IconLocation = f"{icon_path},{icon_index}"
            
            # Save the shortcut
            shortcut.Save()
            
            # Check if the shortcut was created
            if os.path.exists(shortcut_path):
                return True
            else:
                print(f"Shortcut creation failed: {shortcut_path} does not exist after creation attempt")
                return False
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False



