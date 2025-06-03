"""
Creates launcher scripts for games
"""

import os
import configparser

class LauncherCreator:
    """Creates launcher scripts for games"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
    
    def create_launcher(self, game_data, launcher_path):
        """Create a launcher script for the game"""
        try:
            # Get game data
            game_name = game_data.get('name_override', '')
            executable = game_data.get('executable', '')
            directory = game_data.get('directory', '')
            arguments = game_data.get('arguments', '')
            run_as_admin = game_data.get('as_admin', False)
            
            if not game_name or not executable or not directory:
                return False
            
            # Create the launcher content
            launcher_content = self._generate_launcher_script(game_data)
            
            # Create the launcher directory if it doesn't exist
            os.makedirs(os.path.dirname(launcher_path), exist_ok=True)
            
            # Write the launcher script
            with open(launcher_path, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            
            return True
        except Exception as e:
            print(f"Error creating launcher: {str(e)}")
            return False
    
    def _generate_launcher_script(self, game_data):
        """Generate the launcher script content"""
        # Get game data
        game_name = game_data.get('name_override', '')
        executable = game_data.get('executable', '')
        directory = game_data.get('directory', '')
        arguments = game_data.get('arguments', '')
        run_as_admin = game_data.get('as_admin', False)
        
        # Create the basic launcher script
        launcher_content = f"""@echo off
rem Launcher for {game_name}

cd /d "{directory}"

rem Launch the game
"""
        
        # Add the launch command based on admin rights
        if run_as_admin:
            launcher_content += f'powershell -Command "Start-Process \'{executable}\' {arguments} -Verb RunAs"\n'
        else:
            launcher_content += f'start "" "{executable}" {arguments}\n'
        
        # Add exit command
        launcher_content += "\nexit\n"
        
        return launcher_content



