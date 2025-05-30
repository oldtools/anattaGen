"""
Manages creation and updating of game launchers
"""

import os
import shutil
import subprocess
from datetime import datetime

class LauncherManager:
    """Manages the creation and updating of game launchers"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        # Define the template path in the templates directory
        templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'templates'))
        os.makedirs(templates_dir, exist_ok=True)
        self.launcher_template_path = os.path.join(templates_dir, 'launcher.cmd')
        
        # Create the template if it doesn't exist
        if not os.path.exists(self.launcher_template_path):
            self._create_launcher_template()
    
    def _create_launcher_template(self):
        """Create a basic launcher template"""
        basic_template = """@echo off
cd "%~dp0"

REM Game executable and arguments
set GAME_EXE=[GAME_EXE]
set GAME_NAME=[GAME_NAME]
set Exe_Opt=[EXE_OPTIONS]
set Exe_Arg=[EXE_ARGUMENTS]
set RunAsAdmin=[RUN_AS_ADMIN]
set HideTaskbar=[HIDE_TASKBAR]

REM Run the game
cd /d "%~dp0"
if "%RunAsAdmin%" == "1" (
    powershell -Command "Start-Process '%GAME_EXE%' %Exe_Opt% %Exe_Arg% -Verb RunAs"
) else (
    start "" "%GAME_EXE%" %Exe_Opt% %Exe_Arg%
)

exit
"""
        
        try:
            with open(self.launcher_template_path, 'w', encoding='utf-8') as f:
                f.write(basic_template)
            print(f"Created launcher template at {self.launcher_template_path}")
            return True
        except Exception as e:
            print(f"Error creating launcher template: {e}")
            return False
    
    def create_or_update_launcher(self, game_data):
        """Create or update a launcher for the game"""
        # Get the launchers directory from the UI
        launchers_dir = self.main_window.launchers_dir_edit.text()
        if not launchers_dir or not os.path.isdir(launchers_dir):
            print(f"Invalid launchers directory: {launchers_dir}")
            return None
        
        # Get the game name from name_override
        game_name = game_data['name_override']
        if not game_name:
            print(f"Game name not found for {game_data['executable']}")
            return None
        
        # Create the launcher path
        launcher_path = os.path.join(launchers_dir, f"{game_name}.cmd")
        
        # Check if the launcher already exists
        launcher_exists = os.path.exists(launcher_path)
        
        # Create the launcher content
        launcher_content = self._create_launcher_content(game_data)
        if not launcher_content:
            print(f"Failed to create launcher content for {game_name}")
            return None
        
        # Write the launcher file
        try:
            with open(launcher_path, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            
            # Return 'created' or 'updated' based on whether the file existed before
            return 'updated' if launcher_exists else 'created'
        except Exception as e:
            print(f"Error writing launcher file: {e}")
            return None
    
    def _create_launcher_content(self, game_data):
        """Create the content for a launcher file"""
        try:
            # Read the template
            if not os.path.exists(self.launcher_template_path):
                self._create_launcher_template()
            
            with open(self.launcher_template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace placeholders with game data
            content = template_content
            
            # Basic replacements
            content = content.replace("[GAME_EXE]", os.path.join(game_data['directory'], game_data['executable']))
            content = content.replace("[GAME_NAME]", game_data['name_override'])
            
            # Options and arguments
            content = content.replace("[EXE_OPTIONS]", game_data.get('options', ''))
            content = content.replace("[EXE_ARGUMENTS]", game_data.get('arguments', ''))
            
            # Admin and taskbar settings
            content = content.replace("[RUN_AS_ADMIN]", "1" if game_data.get('as_admin', False) else "0")
            content = content.replace("[HIDE_TASKBAR]", "1" if game_data.get('no_tb', False) else "0")
            
            return content
        except Exception as e:
            print(f"Error creating launcher content: {e}")
            return None




