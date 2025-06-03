"""
Manages templates for launcher scripts and configuration files
"""

import os
import re

class TemplateManager:
    """Manages templates for launcher scripts and configuration files"""
    
    def __init__(self):
        """Initialize the template manager"""
        # Get the templates directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.templates_dir = os.path.join(script_dir, "templates")
        
        # Create the templates directory if it doesn't exist
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
        
        # Template file paths
        self.launcher_template_path = os.path.join(self.templates_dir, "launcher_template.set")
        self.game_ini_template_path = os.path.join(self.templates_dir, "game_ini_template.set")
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default templates if they don't exist"""
        # Create launcher template
        if not os.path.exists(self.launcher_template_path):
            self._create_default_launcher_template()
        
        # Create Game.ini template
        if not os.path.exists(self.game_ini_template_path):
            self._create_default_game_ini_template()
    
    def _create_default_launcher_template(self):
        """Create the default launcher template"""
        default_template = """@echo off
setlocal enabledelayedexpansion

rem Launcher for {{GAME_NAME}}

rem Launch sequence
{{LAUNCH_SEQUENCE}}

rem Launch the game
cd /d "{{GAME_DIRECTORY}}"
{{LAUNCH_COMMAND}}

rem Wait for the game to start
timeout /t 3 /nobreak >nul

rem Wait for the game to exit
:wait_loop
tasklist /FI "IMAGENAME eq {{GAME_EXECUTABLE_NAME}}" 2>NUL | find /I /N "{{GAME_EXECUTABLE_NAME}}" >NUL
if "%ERRORLEVEL%"=="0" (
    timeout /t 2 /nobreak >nul
    goto wait_loop
)

rem Exit sequence
{{EXIT_SEQUENCE}}

exit
"""
        try:
            with open(self.launcher_template_path, 'w', encoding='utf-8') as f:
                f.write(default_template)
            print(f"Created default launcher template at {self.launcher_template_path}")
        except Exception as e:
            print(f"Error creating default launcher template: {str(e)}")
    
    def _create_default_game_ini_template(self):
        """Create the default Game.ini template"""
        default_template = """[Game]
Name = {{GAME_NAME}}
Executable = {{GAME_EXECUTABLE}}
Directory = {{GAME_DIRECTORY}}
SteamTitle = {{STEAM_TITLE}}
SteamID = {{STEAM_ID}}
Options = {{GAME_OPTIONS}}
Arguments = {{GAME_ARGUMENTS}}

[Paths]
Player1Profile = {{PLAYER1_PROFILE}}
Player2Profile = {{PLAYER2_PROFILE}}
ControllerMapperApp = {{CONTROLLER_MAPPER_APP}}
MultiMonitorGamingConfig = {{MONITOR_GAMING_CONFIG}}
MultiMonitorMediaConfig = {{MONITOR_MEDIA_CONFIG}}
JustAfterLaunchApp = {{JUST_AFTER_APP}}
JustBeforeExitApp = {{JUST_BEFORE_APP}}
PreLaunchApp1 = {{PRE_LAUNCH_APP1}}
PreLaunchApp2 = {{PRE_LAUNCH_APP2}}
PreLaunchApp3 = {{PRE_LAUNCH_APP3}}
PostLaunchApp1 = {{POST_LAUNCH_APP1}}
PostLaunchApp2 = {{POST_LAUNCH_APP2}}
PostLaunchApp3 = {{POST_LAUNCH_APP3}}
KillListExecutables = {{KILL_LIST_EXECUTABLES}}

[Options]
RunAsAdmin = {{RUN_AS_ADMIN}}
HideTaskbar = {{HIDE_TASKBAR}}
UseKillList = {{USE_KILL_LIST}}
Borderless = {{BORDERLESS}}

[PreLaunch]
PreLaunchApp1RunWait = {{PRE1_RUN_WAIT}}
PreLaunchApp2RunWait = {{PRE2_RUN_WAIT}}
PreLaunchApp3RunWait = {{PRE3_RUN_WAIT}}

[PostLaunch]
PostLaunchApp1RunWait = {{POST1_RUN_WAIT}}
PostLaunchApp2RunWait = {{POST2_RUN_WAIT}}
PostLaunchApp3RunWait = {{POST3_RUN_WAIT}}
JustAfterLaunchAppRunWait = {{JUST_AFTER_RUN_WAIT}}
JustBeforeExitAppRunWait = {{JUST_BEFORE_RUN_WAIT}}

[Sequences]
LaunchSequence = {{LAUNCH_SEQUENCE}}
ExitSequence = {{EXIT_SEQUENCE}}
"""
        try:
            with open(self.game_ini_template_path, 'w', encoding='utf-8') as f:
                f.write(default_template)
            print(f"Created default Game.ini template at {self.game_ini_template_path}")
        except Exception as e:
            print(f"Error creating default Game.ini template: {str(e)}")
    
    def get_launcher_template(self):
        """Get the launcher template content"""
        try:
            with open(self.launcher_template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading launcher template: {str(e)}")
            # Create and return the default template
            self._create_default_launcher_template()
            with open(self.launcher_template_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def get_game_ini_template(self):
        """Get the Game.ini template content"""
        try:
            with open(self.game_ini_template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading Game.ini template: {str(e)}")
            # Create and return the default template
            self._create_default_game_ini_template()
            with open(self.game_ini_template_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def fill_launcher_template(self, template, game_data, launch_sequence=None, exit_sequence=None):
        """
        Fill the launcher template with game data
        
        Args:
            template: The template string
            game_data: Dictionary containing game data
            launch_sequence: List of launch sequence items
            exit_sequence: List of exit sequence items
        
        Returns:
            The filled template string
        """
        # Get game data
        game_name = game_data.get('name_override', '')
        executable = game_data.get('executable', '')
        directory = game_data.get('directory', '')
        arguments = game_data.get('arguments', '')
        run_as_admin = game_data.get('as_admin', False)
        
        # Get the executable name (without path)
        executable_name = os.path.basename(executable)
        
        # Create the launch command
        if run_as_admin:
            launch_command = f'powershell -Command "Start-Process \'{executable}\' {arguments} -Verb RunAs"'
        else:
            launch_command = f'start "" "{executable}" {arguments}'
        
        # Process launch sequence
        launch_sequence_str = ""
        if launch_sequence:
            for item in launch_sequence:
                if item == "Controller-Mapper":
                    launch_sequence_str += "rem Start controller mapper\n"
                    launch_sequence_str += "if exist \"%~dp0\\controller_mapper.txt\" (\n"
                    launch_sequence_str += "    for /f \"tokens=*\" %%a in (%~dp0\\controller_mapper.txt) do (\n"
                    launch_sequence_str += "        start \"\" \"%%a\"\n"
                    launch_sequence_str += "    )\n"
                    launch_sequence_str += ")\n"
                elif item == "Monitor-Config":
                    launch_sequence_str += "rem Configure monitors\n"
                    launch_sequence_str += "if exist \"%~dp0\\monitor_config.txt\" (\n"
                    launch_sequence_str += "    for /f \"tokens=*\" %%a in (%~dp0\\monitor_config.txt) do (\n"
                    launch_sequence_str += "        start \"\" \"%%a\"\n"
                    launch_sequence_str += "    )\n"
                    launch_sequence_str += ")\n"
                elif item == "No-TB":
                    launch_sequence_str += "rem Hide taskbar\n"
                    launch_sequence_str += "if exist \"%~dp0\\hide_taskbar.txt\" (\n"
                    launch_sequence_str += "    for /f \"tokens=*\" %%a in (%~dp0\\hide_taskbar.txt) do (\n"
                    launch_sequence_str += "        start \"\" \"%%a\"\n"
                    launch_sequence_str += "    )\n"
                    launch_sequence_str += ")\n"
                # Add more sequence items as needed
        
        # Process exit sequence
        exit_sequence_str = ""
        if exit_sequence:
            for item in exit_sequence:
                if item == "Controller-Mapper":
                    exit_sequence_str += "rem Start controller mapper\n"
                    exit_sequence_str += "if exist \"%~dp0\\controller_mapper.txt\" (\n"
                    exit_sequence_str += "    for /f \"tokens=*\" %%a in (%~dp0\\controller_mapper.txt) do (\n"
                    exit_sequence_str += "        start \"\" \"%%a\"\n"
                    exit_sequence_str += "    )\n"
                    exit_sequence_str += ")\n"
                elif item == "Monitor-Config":
                    exit_sequence_str += "rem Configure monitors\n"
                    exit_sequence_str += "if exist \"%~dp0\\monitor_config.txt\" (\n"
                    exit_sequence_str += "    for /f \"tokens=*\" %%a in (%~dp0\\monitor_config.txt) do (\n"
                    exit_sequence_str += "        start \"\" \"%%a\"\n"
                    exit_sequence_str += "    )\n"
                    exit_sequence_str += ")\n"
                elif item == "Taskbar":
                    exit_sequence_str += "rem Show taskbar\n"
                    exit_sequence_str += "if exist \"%~dp0\\show_taskbar.txt\" (\n"
                    exit_sequence_str += "    for /f \"tokens=*\" %%a in (%~dp0\\show_taskbar.txt) do (\n"
                    exit_sequence_str += "        start \"\" \"%%a\"\n"
                    exit_sequence_str += "    )\n"
                    exit_sequence_str += ")\n"
                # Add more sequence items as needed
        
        # Replace placeholders in the template
        filled_template = template
        filled_template = filled_template.replace("{{GAME_NAME}}", game_name)
        filled_template = filled_template.replace("{{GAME_DIRECTORY}}", directory)
        filled_template = filled_template.replace("{{GAME_EXECUTABLE_NAME}}", executable_name)
        filled_template = filled_template.replace("{{LAUNCH_COMMAND}}", launch_command)
        filled_template = filled_template.replace("{{LAUNCH_SEQUENCE}}", launch_sequence_str)
        filled_template = filled_template.replace("{{EXIT_SEQUENCE}}", exit_sequence_str)
        
        return filled_template
    
    def fill_game_ini_template(self, template, game_data, profile_folder_path, launch_sequence=None, exit_sequence=None):
        """
        Fill the Game.ini template with game data
        
        Args:
            template: The template string
            game_data: Dictionary containing game data
            profile_folder_path: Path to the profile folder
            launch_sequence: List of launch sequence items
            exit_sequence: List of exit sequence items
        
        Returns:
            The filled template string
        """
        # Get game data
        game_name = game_data.get('name_override', '')
        executable = game_data.get('executable', '')
        directory = game_data.get('directory', '')
        steam_title = game_data.get('steam_title', '')
        steam_id = game_data.get('steam_id', '')
        options = game_data.get('options', '')
        arguments = game_data.get('arguments', '')
        
        # Get options
        run_as_admin = '1' if game_data.get('as_admin', False) else '0'
        hide_taskbar = '1' if game_data.get('no_tb', False) else '0'
        use_kill_list = '1' if game_data.get('use_kill_list', False) else '0'
        
        # Get borderless option
        borderless_value = game_data.get('borderless', '0')
        if borderless_value == 'Yes (Kill on Exit)':
            borderless = 'K'
        elif borderless_value == 'Yes':
            borderless = 'E'
        else:
            borderless = '0'
        
        # Process paths section
        paths_section = ""
        
        # Helper function to process paths
        def process_path(key, field_name):
            path_value = game_data.get(field_name, '')
            if path_value:
                # Handle path markers
                if path_value.startswith('>'):  # Local copy
                    path_without_marker = path_value[1:]
                    if path_without_marker:
                        # Use profile folder path for local copies
                        return f"{key} = {os.path.join(profile_folder_path, os.path.basename(path_without_marker))}\n"
                elif path_value.startswith('<'):  # Central reference
                    path_without_marker = path_value[1:]
                    if path_without_marker:
                        # Use original path for central references
                        return f"{key} = {path_without_marker}\n"
                else:
                    # No marker, use as is (default to central)
                    return f"{key} = {path_value}\n"
            return ""
        
        # Process all path fields
        paths_section += process_path('Player1Profile', 'p1_profile')
        paths_section += process_path('Player2Profile', 'p2_profile')
        paths_section += process_path('ControllerMapperApp', 'desktop_ctrl')
        paths_section += process_path('MultiMonitorGamingConfig', 'game_monitor_cfg')
        paths_section += process_path('MultiMonitorMediaConfig', 'desktop_monitor_cfg')
        paths_section += process_path('JustAfterLaunchApp', 'just_after')
        paths_section += process_path('JustBeforeExitApp', 'just_before')
        
        # Pre-launch apps
        for i in range(1, 4):
            paths_section += process_path(f'PreLaunchApp{i}', f'pre{i}')
            paths_section += f"PreLaunchApp{i}RunWait = {'1' if game_data.get(f'pre{i}_run_wait', False) else '0'}\n"
        
        # Post-launch apps
        for i in range(1, 4):
            paths_section += process_path(f'PostLaunchApp{i}', f'post{i}')
            paths_section += f"PostLaunchApp{i}RunWait = {'1' if game_data.get(f'post{i}_run_wait', False) else '0'}\n"
        
        # Add run wait flags for just after/before apps
        paths_section += f"JustAfterLaunchAppRunWait = {'1' if game_data.get('just_after_run_wait', False) else '0'}\n"
        paths_section += f"JustBeforeExitAppRunWait = {'1' if game_data.get('just_before_run_wait', False) else '0'}\n"
        
        # Add kill list executables
        paths_section += f"KillListExecutables = {game_data.get('kill_list_executables', '')}\n"
        
        # Process sequences
        launch_sequence_str = ','.join(launch_sequence) if launch_sequence else ''
        exit_sequence_str = ','.join(exit_sequence) if exit_sequence else ''
        
        # Replace placeholders in the template
        filled_template = template
        filled_template = filled_template.replace("{{GAME_NAME}}", game_name)
        filled_template = filled_template.replace("{{GAME_EXECUTABLE}}", executable)
        filled_template = filled_template.replace("{{GAME_DIRECTORY}}", directory)
        filled_template = filled_template.replace("{{STEAM_TITLE}}", steam_title)
        filled_template = filled_template.replace("{{STEAM_ID}}", steam_id)
        filled_template = filled_template.replace("{{GAME_OPTIONS}}", options)
        filled_template = filled_template.replace("{{GAME_ARGUMENTS}}", arguments)
        filled_template = filled_template.replace("{{PATHS_SECTION}}", paths_section)
        filled_template = filled_template.replace("{{RUN_AS_ADMIN}}", run_as_admin)
        filled_template = filled_template.replace("{{HIDE_TASKBAR}}", hide_taskbar)
        filled_template = filled_template.replace("{{USE_KILL_LIST}}", use_kill_list)
        filled_template = filled_template.replace("{{BORDERLESS}}", borderless)
        filled_template = filled_template.replace("{{LAUNCH_SEQUENCE}}", launch_sequence_str)
        filled_template = filled_template.replace("{{EXIT_SEQUENCE}}", exit_sequence_str)
        
        return filled_template
