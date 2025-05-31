"""
Handles the creation of launcher scripts for games
"""

import os
import configparser
from PyQt6.QtCore import QCoreApplication

class LauncherCreator:
    """Handles the creation of launcher scripts for games"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
    
    def create_launcher(self, game_data, launch_sequence=None, exit_sequence=None):
        """Create a launcher script for the game"""
        # Get the game name
        game_name = game_data.get('name_override', '')
        if not game_name:
            print(f"Game name not found for {game_data.get('executable', 'unknown')}")
            return {'created': False, 'updated': False}
        
        # Get the launcher directory from config.ini
        bat_launcher_dir = self._get_launcher_directory()
        if not bat_launcher_dir:
            print("Batch Launcher directory not found")
            return {'created': False, 'updated': False}
        
        # Check if the launcher already exists
        bat_launcher_exists = os.path.exists(bat_launcher_dir)
        
        bat_launcher_dir = self._get_bat_launcher_directory()
        if not bat_launcher_dir:
            print("Batch Launcher directory not found")
            return {'created': False, 'updated': False}
        # Create the launcher file path
        bat_launcher_path = os.path.join(bat_launcher_dir, f"{game_name}.bat")
        
        # Check if the batch launcher already exists
        bat_launcher_exists = os.path.exists(bat_launcher_path)
        
        # Generate the launcher script content
        bat_launcher_content = self._generate_bat_launcher_script(game_data, launch_sequence, exit_sequence)
        if not bat_launcher_content:
            print(f"Failed to generate batch launcher script for {game_name}")
            return {'created': False, 'updated': False}
        
        # Create the launcher directory if it doesn't exist
        os.makedirs(bat_launcher_dir, exist_ok=True)
        
        # Write the launcher file
        try:
            with open(bat_launcher_path, 'w', encoding='utf-8') as f:
                f.write(bat_launcher_content)
            
            print(f"Created launcher: {bat_launcher_path}")
            
            # Return whether the launcher was created or updated
            return {'created': not bat_launcher_exists, 'updated': bat_launcher_exists}
        except Exception as e:
            print(f"Error writing batch launcher file: {e}")
            return {'created': False, 'updated': False}

    def _generate_bat_launcher_script(self, game_data, launch_sequence=None, exit_sequence=None):
        """Generate the launcher script content"""
        # Use default sequences if not provided
        if not launch_sequence:
            launch_sequence = [
                "Controller-Mapper", 
                "Monitor-Config", 
                "No-TB", 
                "Pre1", 
                "Pre2", 
                "Pre3", 
                "Borderless"
            ]
        
        if not exit_sequence:
            exit_sequence = [
                "Post1", 
                "Post2", 
                "Post3", 
                "Monitor-Config", 
                "Taskbar",
                "Controller-Mapper"
            ]
        
        # Get the game data
        game_name = game_data.get('name_override', '')
        executable = game_data.get('executable', '')
        directory = game_data.get('directory', '')
        arguments = game_data.get('arguments', '')
        
        # Generate the script content
        script_content = "@echo off\n"
        script_content += "setlocal enabledelayedexpansion\n\n"
        
        # Add the game name as a comment
        script_content += f"rem Launcher for {game_name}\n\n"
        
        # Add the launch sequence
        script_content += "rem Launch sequence\n"
        for item in launch_sequence:
            if item == "Controller-Mapper":
                script_content += "rem Start controller mapper\n"
                script_content += "if exist \"%~dp0\\controller_mapper.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\controller_mapper.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Monitor-Config":
                script_content += "rem Configure monitors\n"
                script_content += "if exist \"%~dp0\\monitor_config.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\monitor_config.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "No-TB":
                script_content += "rem Hide taskbar\n"
                script_content += "if exist \"%~dp0\\hide_taskbar.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\hide_taskbar.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Pre1":
                script_content += "rem Pre-launch app 1\n"
                script_content += "if exist \"%~dp0\\pre1.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\pre1.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Pre2":
                script_content += "rem Pre-launch app 2\n"
                script_content += "if exist \"%~dp0\\pre2.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\pre2.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Pre3":
                script_content += "rem Pre-launch app 3\n"
                script_content += "if exist \"%~dp0\\pre3.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\pre3.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Borderless":
                script_content += "rem Start borderless windowing\n"
                script_content += "if exist \"%~dp0\\borderless.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\borderless.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
        
        # Add the game launch
        script_content += "\nrem Launch the game\n"
        script_content += f"cd /d \"{directory}\"\n"
        
        # Check if we need to run as admin
        if game_data.get('as_admin', False):
            script_content += f"powershell -Command \"Start-Process '{os.path.join(directory, executable)}' {arguments} -Verb RunAs\"\n"
        else:
            script_content += f"start \"\" \"{os.path.join(directory, executable)}\" {arguments}\n"
        
        # Wait for the game to exit
        script_content += "\nrem Wait for the game to exit\n"
        script_content += f"echo Waiting for {executable} to exit...\n"
        script_content += f":wait_loop\n"
        script_content += f"tasklist /FI \"IMAGENAME eq {executable}\" 2>NUL | find /I /N \"{executable}\">NUL\n"
        script_content += f"if \"%ERRORLEVEL%\"==\"0\" (\n"
        script_content += f"    timeout /t 2 /nobreak >NUL\n"
        script_content += f"    goto wait_loop\n"
        script_content += f")\n"
        
        # Add the exit sequence
        script_content += "\nrem Exit sequence\n"
        for item in exit_sequence:
            if item == "Post1":
                script_content += "rem Post-exit app 1\n"
                script_content += "if exist \"%~dp0\\post1.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\post1.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Post2":
                script_content += "rem Post-exit app 2\n"
                script_content += "if exist \"%~dp0\\post2.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\post2.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Post3":
                script_content += "rem Post-exit app 3\n"
                script_content += "if exist \"%~dp0\\post3.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\post3.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Monitor-Config":
                script_content += "rem Restore monitor configuration\n"
                script_content += "if exist \"%~dp0\\restore_monitor.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\restore_monitor.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Taskbar":
                script_content += "rem Show taskbar\n"
                script_content += "if exist \"%~dp0\\show_taskbar.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\show_taskbar.txt) do (\n"
                script_content += "        start \"\" \"%%a\"\n"
                script_content += "    )\n"
                script_content += ")\n"
            elif item == "Controller-Mapper":
                script_content += "rem Close controller mapper\n"
                script_content += "if exist \"%~dp0\\controller_mapper.txt\" (\n"
                script_content += "    for /f \"tokens=*\" %%a in (%~dp0\\controller_mapper.txt) do (\n"
                script_content += "        for %%b in (\"%%~nxa\") do (\n"
                script_content += "            taskkill /f /im \"%%~b\" >NUL 2>&1\n"
                script_content += "        )\n"
                script_content += "    )\n"
                script_content += ")\n"
        
        script_content += "\nendlocal\n"
        
        return script_content

    def _get_launcher_directory(self):
        """Get the launcher directory from config.ini"""
        try:
            config = configparser.ConfigParser()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            config_path = os.path.join(app_root_dir, "config.ini")
            
            if not os.path.exists(config_path):
                print(f"Configuration file not found: {config_path}")
                return None
            
            config.read(config_path, encoding='utf-8')
            
            if 'Element Locations' in config and 'launchers_directory' in config['Element Locations']:
                launcher_dir = config['Element Locations']['launchers_directory']
                if os.path.isdir(launcher_dir):
                    launcher_path = launcher_dir
                    return launcher_dir
                else:
                    print(f"Launcher directory does not exist: {launcher_dir}")
                    return None
            else:
                print("Launcher directory not found in config.ini")
                return None
        except Exception as e:
                    print(f"Error getting launcher directory: {e}")
                    return None

        # Get profiles directory from config
    def _get_bat_launcher_directory(self):
        try:
            config = configparser.ConfigParser()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            config_path = os.path.join(app_root_dir, "config.ini")
            
            # Get the game name
            game_name = game_data.get('name_override', '')
            if not game_name:
                print(f"Game name not found for {game_data.get('executable', 'unknown')}")
                return game_stats
            
            else:
                print("Batch Launcher directory not found in config.ini")
                return None
                    
            if not os.path.exists(config_path):
                print(f"Configuration file not found: {config_path}")
                return None
                
            config.read(config_path, encoding='utf-8')
            bat_launcher_dir = None
            if 'Element Locations' in config and 'profiles_directory' in config['Element Locations']:
                bat_launchers_dir = config['Element Locations']['profiles_directory']
                if os.path.isdir(launcher_dir):
                    return bat_launcher_dir
                else:
                    print(f"Batch Launcher directory does not exist: {bat_auncher_dir}")
                    return None
            else:
                print("Batch Launcher directory not found in config.ini")
                return None
        except Exception as e:
                    print(f"Error getting Batch launcher directory: {e}")
                    return None
