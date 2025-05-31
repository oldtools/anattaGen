"""
Handles writing configuration files for games
"""

import os
import configparser
from PyQt6.QtCore import QCoreApplication

class ConfigWriter:
    """Handles writing configuration files for games"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
    
    def process_game_config(self, game_data, create_profile_folders, launch_sequence=None, exit_sequence=None):
        """Create or update the Game.ini configuration file"""
        # Get the profiles directory
        profiles_dir = self.main_window.profiles_dir_edit.text() if hasattr(self.main_window, 'profiles_dir_edit') else None
        
        # Try to get profiles directory from config if not available in UI
        if not profiles_dir or not os.path.isdir(profiles_dir):
            try:
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
            return {'created': False, 'updated': False}
        
        # Get the game name
        game_name = game_data.get('name_override', '')
        if not game_name:
            print(f"Game name not found for {game_data.get('executable', 'unknown')}")
            return {'created': False, 'updated': False}
        
        # Create the profile folder path
        profile_folder_path = os.path.join(profiles_dir, game_name)
        
        # Create the profile folder if it doesn't exist
        if create_profile_folders and not os.path.exists(profile_folder_path):
            try:
                os.makedirs(profile_folder_path)
                print(f"Created profile folder: {profile_folder_path}")
            except Exception as e:
                print(f"Error creating profile folder: {e}")
                return {'created': False, 'updated': False}
        
        # Create the Game.ini file path
        game_ini_path = os.path.join(profile_folder_path, "Game.ini")
        
        # Check if the Game.ini file exists
        game_ini_exists = os.path.exists(game_ini_path)
        
        # Create or update the Game.ini file
        config = configparser.ConfigParser()
        
        # Read the existing file if it exists
        if game_ini_exists:
            try:
                config.read(game_ini_path, encoding='utf-8')
            except Exception as e:
                print(f"Error reading existing Game.ini: {e}")
        
        # Ensure all sections exist
        for section in ['Game', 'Paths', 'Options', 'PreLaunch', 'PostLaunch', 'Sequences']:
            if section not in config:
                config[section] = {}
        
        # Update the Game section
        game_section = config['Game']
        game_section['Name'] = game_name
        game_section['Executable'] = game_data['executable']
        game_section['Directory'] = game_data['directory']
        game_section['SteamTitle'] = game_data.get('steam_title', '')
        game_section['SteamID'] = game_data.get('steam_id', '')
        game_section['Options'] = game_data.get('options', '')
        game_section['Arguments'] = game_data.get('arguments', '')
        
        # Update the Options section
        options_section = config['Options']
        options_section['RunAsAdmin'] = '1' if game_data.get('as_admin', False) else '0'
        options_section['HideTaskbar'] = '1' if game_data.get('no_tb', False) else '0'
        
        # Add UseKillList option
        if hasattr(self.main_window, 'use_kill_list_checkbox'):
            options_section['UseKillList'] = '1' if self.main_window.use_kill_list_checkbox.isChecked() else '0'
        else:
            # Default to '0' if checkbox not found
            options_section['UseKillList'] = '0'
        
        # Add Borderless option
        if hasattr(self.main_window, 'enable_borderless_windowing_checkbox'):
            if self.main_window.enable_borderless_windowing_checkbox.isChecked():
                if hasattr(self.main_window, 'terminate_bw_on_exit_checkbox') and self.main_window.terminate_bw_on_exit_checkbox.isChecked():
                    options_section['Borderless'] = 'K'  # K for terminates on exit
                else:
                    options_section['Borderless'] = 'E'  # E for enabled
            else:
                options_section['Borderless'] = '0'  # 0 for disabled
        else:
            # Default to '0' if checkbox not found
            options_section['Borderless'] = '0'
        
        # Update the Paths section with paths from the UI
        paths_section = config['Paths']
        
        # Add controller mapper app
        if hasattr(self.main_window, 'controller_mapper_app_line_edit'):
            controller_app = self.main_window.controller_mapper_app_line_edit.text()
            if controller_app:
                # Remove '>' marker if present
                if controller_app.startswith('>'):
                    controller_app = controller_app[1:]
                paths_section['ControllerMapperApp'] = controller_app
        
        # Add borderless windowing app
        if hasattr(self.main_window, 'borderless_app_line_edit'):
            borderless_app = self.main_window.borderless_app_line_edit.text()
            if borderless_app:
                # Remove '>' marker if present
                if borderless_app.startswith('>'):
                    borderless_app = borderless_app[1:]
                paths_section['BorderlessWindowingApp'] = borderless_app
        
        # Add multi-monitor tool
        if hasattr(self.main_window, 'multimonitor_app_line_edit'):
            mm_tool = self.main_window.multimonitor_app_line_edit.text()
            if mm_tool:
                # Remove '>' marker if present
                if mm_tool.startswith('>'):
                    mm_tool = mm_tool[1:]
                paths_section['MultiMonitorTool'] = mm_tool
        
        # Add multi-monitor gaming config
        if hasattr(self.main_window, 'multimonitor_gaming_config_edit'):
            mm_gaming_config = self.main_window.multimonitor_gaming_config_edit.text()
            if mm_gaming_config:
                # Remove '>' marker if present
                if mm_gaming_config.startswith('>'):
                    mm_gaming_config = mm_gaming_config[1:]
                paths_section['MultiMonitorGamingConfig'] = mm_gaming_config
        
        # Add player profiles
        if hasattr(self.main_window, 'p1_profile_edit'):
            p1_profile = self.main_window.p1_profile_edit.text()
            if p1_profile:
                # Remove '>' marker if present
                if p1_profile.startswith('>'):
                    p1_profile = p1_profile[1:]
                paths_section['Player1Profile'] = p1_profile
        
        if hasattr(self.main_window, 'p2_profile_edit'):
            p2_profile = self.main_window.p2_profile_edit.text()
            if p2_profile:
                # Remove '>' marker if present
                if p2_profile.startswith('>'):
                    p2_profile = p2_profile[1:]
                paths_section['Player2Profile'] = p2_profile
        
        # Add pre-launch apps
        if hasattr(self.main_window, 'pre_launch_app_line_edits'):
            for i, le in enumerate(self.main_window.pre_launch_app_line_edits):
                pre_launch_app = le.text()
                if pre_launch_app:
                    # Remove '>' marker if present
                    if pre_launch_app.startswith('>'):
                        pre_launch_app = pre_launch_app[1:]
                    paths_section[f'PreLaunchApp{i+1}'] = pre_launch_app
        
        # Add post-launch apps
        if hasattr(self.main_window, 'post_launch_app_line_edits'):
            for i, le in enumerate(self.main_window.post_launch_app_line_edits):
                post_launch_app = le.text()
                if post_launch_app:
                    # Remove '>' marker if present
                    if post_launch_app.startswith('>'):
                        post_launch_app = post_launch_app[1:]
                    paths_section[f'PostLaunchApp{i+1}'] = post_launch_app
        
        # Add just after launch app
        if hasattr(self.main_window, 'after_launch_app_line_edit'):
            after_launch_app = self.main_window.after_launch_app_line_edit.text()
            if after_launch_app:
                # Remove '>' marker if present
                if after_launch_app.startswith('>'):
                    after_launch_app = after_launch_app[1:]
                paths_section['JustAfterLaunchApp'] = after_launch_app
        
        # Add just before exit app
        if hasattr(self.main_window, 'before_exit_app_line_edit'):
            before_exit_app = self.main_window.before_exit_app_line_edit.text()
            if before_exit_app:
                # Remove '>' marker if present
                if before_exit_app.startswith('>'):
                    before_exit_app = before_exit_app[1:]
                paths_section['JustBeforeExitApp'] = before_exit_app
        
        # Add kill list executables (even if empty)
        paths_section['KillListExecutables'] = ''
        
        # Add run wait flags for apps
        if hasattr(self.main_window, 'after_launch_run_wait_checkbox'):
            paths_section['JustAfterLaunchAppRunWait'] = '1' if self.main_window.after_launch_run_wait_checkbox.isChecked() else '0'
        
        if hasattr(self.main_window, 'before_exit_run_wait_checkbox'):
            paths_section['JustBeforeExitAppRunWait'] = '1' if self.main_window.before_exit_run_wait_checkbox.isChecked() else '0'
        
        if hasattr(self.main_window, 'pre_launch_run_wait_checkboxes'):
            for i, cb in enumerate(self.main_window.pre_launch_run_wait_checkboxes):
                paths_section[f'PreLaunchApp{i+1}RunWait'] = '1' if cb.isChecked() else '0'
        
        if hasattr(self.main_window, 'post_launch_run_wait_checkboxes'):
            for i, cb in enumerate(self.main_window.post_launch_run_wait_checkboxes):
                paths_section[f'PostLaunchApp{i+1}RunWait'] = '1' if cb.isChecked() else '0'
        
        # Update the Sequences section with launch and exit sequences
        sequences_section = config['Sequences']
        
        # Save launch sequence
        if launch_sequence:
            sequences_section['LaunchSequence'] = ','.join(launch_sequence)
        
        # Save exit sequence
        if exit_sequence:
            sequences_section['ExitSequence'] = ','.join(exit_sequence)
        
        # Write the Game.ini file
        try:
            with open(game_ini_path, 'w', encoding='utf-8') as f:
                config.write(f)
            print(f"{'Updated' if game_ini_exists else 'Created'} Game.ini: {game_ini_path}")
            return {'created': not game_ini_exists, 'updated': game_ini_exists}
        except Exception as e:
            print(f"Error writing Game.ini: {e}")
            return {'created': False, 'updated': False}

