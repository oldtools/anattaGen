"""
Manages creation of shortcuts for games and launchers
"""

import os
import sys
import subprocess
import re

# Try to import Windows-specific modules, use fallbacks if not available
try:
    import winshell
    from win32com.client import Dispatch
    WINDOWS_MODULES_AVAILABLE = True
except ImportError:
    WINDOWS_MODULES_AVAILABLE = False

class ShortcutManager:
    """Manages creation of shortcuts for games and launchers"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        self.debug = True  # Enable debug output
    
    def debug_print(self, message):
        """Print debug messages if debug is enabled"""
        if self.debug:
            print(f"ShortcutManager: {message}")
    
    def create_shortcuts(self, game_data, profile_folder_path, launcher_path):
        """Create shortcuts for both game and launcher"""
        try:
            self.debug_print(f"Creating shortcuts for {game_data.get('name_override', '')}")
            self.debug_print(f"Profile folder: {profile_folder_path}")
            self.debug_print(f"Launcher path: {launcher_path}")
            
            # Create game shortcut
            game_shortcut_result = self._create_game_shortcut(game_data, profile_folder_path)
            
            # Create launcher shortcut
            launcher_shortcut_result = self._create_launcher_shortcut(game_data, profile_folder_path, launcher_path)
            
            return True
        except Exception as e:
            self.debug_print(f"Error creating shortcuts: {str(e)}")
            return False
    
    def _create_game_shortcut(self, game_data, profile_folder_path):
        """Create a shortcut to the game in the profile folder"""
        try:
            # Get game data
            game_name = game_data.get('name_override', '')
            executable = game_data.get('executable', '')
            directory = game_data.get('directory', '')
            arguments = game_data.get('arguments', '')
            
            self.debug_print(f"Creating game shortcut for {game_name}")
            self.debug_print(f"Executable: {executable}")
            self.debug_print(f"Directory: {directory}")
            self.debug_print(f"Arguments: {arguments}")
            
            if not game_name or not executable or not directory:
                self.debug_print("Missing required game data")
                return False
            
            # Create the shortcut path - use the original game name for the directory
            shortcut_path = os.path.join(profile_folder_path, f"{game_name}.lnk")
            self.debug_print(f"Shortcut path: {shortcut_path}")
            
            # Ensure the executable and directory paths exist and are absolute
            if not os.path.isabs(executable):
                executable = os.path.abspath(executable)
                self.debug_print(f"Converted executable to absolute path: {executable}")
            
            if not os.path.isabs(directory):
                directory = os.path.abspath(directory)
                self.debug_print(f"Converted directory to absolute path: {directory}")
            
            # Try Windows COM method first
            if WINDOWS_MODULES_AVAILABLE:
                try:
                    self.debug_print("Attempting to create shortcut using Windows COM")
                    # Create the shortcut using Windows COM
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.TargetPath = executable
                    shortcut.WorkingDirectory = directory
                    shortcut.Arguments = arguments
                    shortcut.save()
                    self.debug_print("Successfully created game shortcut using Windows COM")
                    return True
                except Exception as e:
                    self.debug_print(f"Windows COM shortcut creation failed: {str(e)}")
                    self.debug_print("Falling back to alternative method")
            else:
                self.debug_print("Windows modules not available, using fallback method")
            
            # Use fallback method if Windows COM failed or is not available
            self._create_shortcut_fallback(executable, directory, arguments, shortcut_path)
            return True
            
        except Exception as e:
            self.debug_print(f"Error creating game shortcut: {str(e)}")
            # Try fallback as last resort
            try:
                self.debug_print("Attempting last-resort fallback for game shortcut")
                self._create_shortcut_fallback(executable, directory, arguments, shortcut_path)
                return True
            except Exception as fallback_error:
                self.debug_print(f"Fallback also failed: {str(fallback_error)}")
                return False
    
    def _create_launcher_shortcut(self, game_data, profile_folder_path, launcher_path):
        """Create a shortcut to the launcher in the profile folder"""
        try:
            # Get game data
            game_name = game_data.get('name_override', '')
            
            self.debug_print(f"Creating launcher shortcut for {game_name}")
            self.debug_print(f"Launcher path: {launcher_path}")
            
            if not game_name or not launcher_path:
                self.debug_print("Missing required launcher data")
                return False
            
            # Create the shortcut path - use the original game name for the directory
            shortcut_path = os.path.join(profile_folder_path, f"{game_name} Launcher.lnk")
            self.debug_print(f"Launcher shortcut path: {shortcut_path}")
            
            # Ensure the launcher path exists and is absolute
            if not os.path.isabs(launcher_path):
                launcher_path = os.path.abspath(launcher_path)
                self.debug_print(f"Converted launcher path to absolute: {launcher_path}")
            
            # Ensure the launcher exists
            if not os.path.exists(launcher_path):
                self.debug_print(f"Warning: Launcher does not exist: {launcher_path}")
                # Create an empty launcher file if it doesn't exist
                os.makedirs(os.path.dirname(launcher_path), exist_ok=True)
                with open(launcher_path, 'w', encoding='utf-8') as f:
                    f.write('@echo off\necho Launcher placeholder\npause\n')
                self.debug_print(f"Created placeholder launcher file")
            
            # Try Windows COM method first
            if WINDOWS_MODULES_AVAILABLE:
                try:
                    self.debug_print("Attempting to create launcher shortcut using Windows COM")
                    # Create the shortcut using Windows COM
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.TargetPath = launcher_path
                    shortcut.WorkingDirectory = os.path.dirname(launcher_path)
                    shortcut.save()
                    self.debug_print("Successfully created launcher shortcut using Windows COM")
                    return True
                except Exception as e:
                    self.debug_print(f"Windows COM launcher shortcut creation failed: {str(e)}")
                    self.debug_print("Falling back to alternative method")
            else:
                self.debug_print("Windows modules not available, using fallback method")
            
            # Use fallback method if Windows COM failed or is not available
            self._create_shortcut_fallback(launcher_path, os.path.dirname(launcher_path), "", shortcut_path)
            return True
            
        except Exception as e:
            self.debug_print(f"Error creating launcher shortcut: {str(e)}")
            # Try fallback as last resort
            try:
                self.debug_print("Attempting last-resort fallback for launcher shortcut")
                self._create_shortcut_fallback(launcher_path, os.path.dirname(launcher_path), "", shortcut_path)
                return True
            except Exception as fallback_error:
                self.debug_print(f"Fallback also failed: {str(fallback_error)}")
                return False
    
    def _create_shortcut_fallback(self, target, working_dir, arguments, shortcut_path):
        """Create a shortcut using alternative methods when Windows modules aren't available"""
        try:
            self.debug_print(f"Creating fallback shortcut for {target} at {shortcut_path}")
            
            # Check if we're on Windows
            if sys.platform == 'win32':
                # Try using the Shortcut.exe utility if available
                script_dir = os.path.dirname(os.path.abspath(__file__))
                app_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
                shortcut_exe = os.path.join(app_root_dir, "bin", "Shortcut.exe")
                
                if os.path.exists(shortcut_exe):
                    # Use Shortcut.exe to create the shortcut
                    self.debug_print(f"Using Shortcut.exe: {shortcut_exe}")
                    cmd = [
                        shortcut_exe,
                        "/F:" + shortcut_path,
                        "/A:C",
                        "/T:" + target
                    ]
                    
                    if working_dir:
                        cmd.append("/W:" + working_dir)
                    
                    if arguments:
                        cmd.append("/P:" + arguments)
                    
                    self.debug_print(f"Running command: {' '.join(cmd)}")
                    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
                    if result.returncode != 0:
                        self.debug_print(f"Shortcut.exe failed: {result.stderr}")
                        raise Exception(f"Shortcut.exe failed with code {result.returncode}")
                    else:
                        self.debug_print("Shortcut.exe succeeded")
                else:
                    # Create a simple batch file as a fallback
                    self.debug_print(f"Shortcut.exe not found, creating batch file instead")
                    batch_path = shortcut_path.replace('.lnk', '.bat')
                    with open(batch_path, 'w', encoding='utf-8') as f:
                        f.write(f'@echo off\ncd /d "{working_dir}"\nstart "" "{target}" {arguments}\n')
                    self.debug_print(f"Created batch file: {batch_path}")
            else:
                # For Linux/Mac, create a shell script
                self.debug_print(f"Creating shell script for non-Windows platform")
                shell_path = shortcut_path.replace('.lnk', '.sh')
                with open(shell_path, 'w', encoding='utf-8') as f:
                    f.write(f'#!/bin/bash\ncd "{working_dir}"\n"{target}" {arguments}\n')
                # Make it executable
                os.chmod(shell_path, 0o755)
                self.debug_print(f"Created shell script: {shell_path}")
            
            return True
        except Exception as e:
            self.debug_print(f"Error in shortcut fallback: {str(e)}")
            # Create a text file as an absolute last resort
            try:
                txt_path = shortcut_path.replace('.lnk', '.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"Target: {target}\nWorking Directory: {working_dir}\nArguments: {arguments}\n")
                self.debug_print(f"Created text file as last resort: {txt_path}")
                return True
            except Exception as txt_error:
                self.debug_print(f"Text file creation also failed: {str(txt_error)}")
                return False


