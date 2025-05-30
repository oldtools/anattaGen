"""
Manages creation of Windows shortcuts (.lnk files) and platform-specific alternatives
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

class ShortcutManager:
    """Manages the creation of shortcuts for games and launchers"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        
        # Path to launcher.exe in the bin directory
        self.launcher_exe_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'bin', 'launcher.exe'
        ))
        
        # Check if the launcher.exe exists
        if not os.path.exists(self.launcher_exe_path):
            print(f"Warning: launcher.exe not found at {self.launcher_exe_path}")
            
            # Try to find launcher.exe in the app directory
            app_directory = getattr(main_window, 'app_directory', None)
            if app_directory:
                alt_launcher_path = os.path.join(app_directory, 'bin', 'launcher.exe')
                if os.path.exists(alt_launcher_path):
                    self.launcher_exe_path = alt_launcher_path
                    print(f"Found launcher.exe at {self.launcher_exe_path}")
    
    def create_game_shortcut(self, game_data, profile_folder_path):
        """Create a shortcut to the game in the profile folder"""
        # Get the game name from name_override
        game_name = game_data['name_override']
        if not game_name:
            print(f"Game name not found for {game_data['executable']}")
            return False
        
        # Get the game executable path
        game_exe_path = os.path.join(game_data['directory'], game_data['executable'])
        if not os.path.exists(game_exe_path):
            print(f"Game executable not found: {game_exe_path}")
            return False
        
        # Create the shortcut path
        shortcut_path = os.path.join(profile_folder_path, f"{game_name}.lnk")
        
        # Create the shortcut
        if sys.platform == 'win32':
            try:
                # Create a direct shortcut to the game executable
                return self._create_windows_shortcut(
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
            # For non-Windows platforms, create a symlink
            try:
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
                os.symlink(game_exe_path, shortcut_path)
                return True
            except Exception as e:
                print(f"Error creating game symlink: {e}")
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
        
        # Create the shortcut
        if sys.platform == 'win32':
            try:
                # Create a shortcut to launcher.exe with the profile shortcut as argument
                return self._create_windows_shortcut(
                    launcher_shortcut_path,
                    self.launcher_exe_path,  # Target is launcher.exe
                    profile_folder_path,     # Working directory is the profile folder
                    profile_shortcut_path,   # Argument is the profile shortcut (no quotes)
                    game_exe_path,           # Icon from the game executable
                    0                        # Icon index
                )
            except Exception as e:
                print(f"Error creating launcher shortcut: {e}")
                return False
        else:
            # For non-Windows platforms, create a symlink to the launcher
            try:
                if os.path.exists(launcher_shortcut_path):
                    os.remove(launcher_shortcut_path)
                # Create a symlink to the launcher with the profile shortcut as the target
                os.symlink(self.launcher_exe_path, launcher_shortcut_path)
                return True
            except Exception as e:
                print(f"Error creating launcher symlink: {e}")
                return False
    
    def _create_windows_shortcut(self, shortcut_path, target_path, working_dir, arguments, icon_path, icon_index):
        """Create a Windows shortcut (.lnk file)"""
        try:
            # Create a temporary VBS file
            vbs_file = tempfile.NamedTemporaryFile(delete=False, suffix='.vbs')
            vbs_path = vbs_file.name
            vbs_file.close()
            
            # Prepare the VBS script content - use single quotes to avoid escaping issues
            vbs_content = f'''
Set WshShell = CreateObject("WScript.Shell")
Set oShellLink = WshShell.CreateShortcut("{shortcut_path}")
oShellLink.TargetPath = "{target_path}"
oShellLink.WorkingDirectory = "{working_dir}"
oShellLink.Arguments = "{arguments}"
oShellLink.IconLocation = "{icon_path}, {icon_index}"
oShellLink.Save
'''
            
            # Write the VBS script
            with open(vbs_path, 'w', encoding='utf-8') as f:
                f.write(vbs_content)
            
            # Execute the VBS script
            subprocess.run(['cscript', '//nologo', vbs_path], check=True)
            
            # Clean up the temporary file
            try:
                os.unlink(vbs_path)
            except:
                pass
            
            return True
        except Exception as e:
            print(f"Error creating shortcut with VBS: {e}")
            return False











