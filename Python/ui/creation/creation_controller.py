"""
Controls the creation process for game profiles and launchers
"""

import os
import configparser
import shutil
from PyQt6.QtWidgets import QCheckBox, QMessageBox, QProgressDialog
from PyQt6.QtCore import QCoreApplication, Qt

from .shortcut_manager import ShortcutManager
from .launcher_creator import LauncherCreator
from Python.ui.creation.game_data_fetcher import GameDataFetcher

class CreationController:
    """Controls the creation process for game profiles and launchers"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        self.shortcut_manager = ShortcutManager(main_window)
        self.launcher_creator = LauncherCreator(main_window)

        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.app_directory = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        self.max_file_size = 181 * 1024  # 181 KB
    
    def create_all(self, selected_games):
        """Process all selected games"""
        # Initialize counters
        processed_count = 0
        failed_count = 0
        
        # Process each game
        for game_data in selected_games:
            # Debug output to verify game data
            print(f"\nProcessing game: {game_data.get('name_override', '')}")
            print(f"Executable: {game_data.get('executable', '')}")
            print(f"Directory: {game_data.get('directory', '')}")
            
            # Debug output for path columns
            path_columns = [
                "p1_profile", "p2_profile", "desktop_ctrl", 
                "game_monitor_cfg", "desktop_monitor_cfg", 
                "post1", "post2", "post3", 
                "pre1", "pre2", "pre3", 
                "just_after", "just_before"
            ]
            
            for field in path_columns:
                value = game_data.get(field, '')
                print(f"{field}: {value}")
            
            # Process the game
            result = self._process_game(game_data)
            
            # Update counters
            if result:
                processed_count += 1
            else:
                failed_count += 1
        
        # Return the results
        return {
            'processed_count': processed_count,
            'failed_count': failed_count
        }
    
    def _process_game(self, game_data):
        """Process a single game following the exact steps specified"""
        try:
            # Get configuration from config.ini
            config = self._get_config()
            if not config:
                print("Failed to load configuration")
                return False
            
            # Get profiles directory from config
            profiles_dir = None
            if 'Element Locations' in config and 'profiles_directory' in config['Element Locations']:
                profiles_dir = config['Element Locations']['profiles_directory']
            
            if not profiles_dir or not os.path.isdir(profiles_dir):
                print("Profiles directory not found or invalid")
                return False
            
            # Get launcher directory from config
            launcher_dir = None
            if 'Element Locations' in config and 'launchers_directory' in config['Element Locations']:
                launcher_dir = config['Element Locations']['launchers_directory']
            
            if not launcher_dir or not os.path.isdir(launcher_dir):
                print("Launcher directory not found or invalid")
                return False
            
            # Get the game name
            game_name = game_data.get('name_override', '')
            if not game_name:
                print("Game name not provided")
                return False
            
            # Step 4a: Create the profile folder
            profile_folder_path = os.path.join(profiles_dir, game_name)
            os.makedirs(profile_folder_path, exist_ok=True)
            
            # Step 4b: Create Game.ini with basic information (columns 1-7, 21-23)
            game_ini_result = self._create_game_ini(game_data, profile_folder_path, profiles_dir, launcher_dir)
            if not game_ini_result:
                print(f"Failed to create Game.ini for {game_name}")
                return False
            
            # Fetch additional game data in the background
            self._fetch_additional_game_data(game_data, profile_folder_path)
            
            # Process path columns (8-20) before creating launcher and shortcuts
            path_processing_result = self._process_path_columns(game_data, profile_folder_path, config)
            if not path_processing_result:
                print(f"Failed to process path columns for {game_name}")
                return False
            
            # Step 4c: Create launcher and shortcuts (moved to the end)
            launcher_path = os.path.join(launcher_dir, f"{game_name}.cmd")
            
            # Create the launcher directory if it doesn't exist
            os.makedirs(os.path.dirname(launcher_path), exist_ok=True)
            
            # Create the launcher
            launcher_result = self.launcher_creator.create_launcher(game_data, launcher_path)
            if not launcher_result:
                print(f"Failed to create launcher for {game_name}")
                # Continue anyway, as this is not critical
            
            # Create shortcuts
            shortcut_result = self.shortcut_manager.create_shortcuts(game_data, profile_folder_path, launcher_path)
            if not shortcut_result:
                print(f"Failed to create shortcuts for {game_name}")
                # Continue anyway, as this is not critical
            
            return True
        except Exception as e:
            print(f"Error processing game {game_data.get('name_override', '')}: {str(e)}")
            return False
    
    def _create_game_ini(self, game_data, profile_folder_path, profiles_dir, launcher_dir):
        """Create Game.ini with basic information and key variables"""
        try:
            # Create a new config file
            config = configparser.ConfigParser()
            config.optionxform = str  # Preserve case for keys
            
            # Ensure all sections exist
            for section in ['Game', 'Paths', 'Options', 'PreLaunch', 'PostLaunch', 'Sequences']:
                config[section] = {}
            
            # Get the game name
            game_name = game_data.get('name_override', '')
            
            # Update the Game section with columns 1-7
            game_section = config['Game']
            game_section['Name'] = game_name
            game_section['Executable'] = game_data.get('executable', '')
            game_section['Directory'] = game_data.get('directory', '')
            game_section['SteamTitle'] = game_data.get('steam_title', '')
            game_section['SteamID'] = game_data.get('steam_id', '')
            game_section['Options'] = game_data.get('options', '')
            game_section['Arguments'] = game_data.get('arguments', '')
            
            # Update the Options section with columns 21-23
            options_section = config['Options']
            options_section['RunAsAdmin'] = '1' if game_data.get('as_admin', False) else '0'
            options_section['HideTaskbar'] = '1' if game_data.get('no_tb', False) else '0'
            options_section['UseKillList'] = '0'  # Default value
            
            # Add Borderless option
            borderless_value = game_data.get('borderless', '0')
            if borderless_value == 'Yes (Kill on Exit)':
                options_section['Borderless'] = 'K'
            elif borderless_value == 'Yes':
                options_section['Borderless'] = 'E'
            else:
                options_section['Borderless'] = '0'
            
            # Add key variables
            paths_section = config['Paths']
            paths_section['ProfilePath'] = profile_folder_path
            paths_section['LauncherPath'] = os.path.join(launcher_dir, f"{game_name}.cmd")
            
            # Add columns 8-20 directly to ensure they're included
            column_mapping = {
                'p1_profile': 'Player1Profile',
                'p2_profile': 'Player2Profile',
                'desktop_ctrl': 'ControllerMapperApp',
                'game_monitor_cfg': 'MultiMonitorGamingConfig',
                'desktop_monitor_cfg': 'MultiMonitorMediaConfig',
                'post1': 'PostLaunchApp1',
                'post2': 'PostLaunchApp2',
                'post3': 'PostLaunchApp3',
                'pre1': 'PreLaunchApp1',
                'pre2': 'PreLaunchApp2',
                'pre3': 'PreLaunchApp3',
                'just_after': 'JustAfterLaunchApp',
                'just_before': 'JustBeforeExitApp'
            }
            
            # Add initial values for columns 8-20
            for column_key, ini_key in column_mapping.items():
                value = game_data.get(column_key, '')
                if value:
                    print(f"Initial Game.ini setting: {ini_key} = {value}")
                    # Store the raw value initially
                    if value.startswith('<') or value.startswith('>'):
                        # For special indicators, store without the indicator for now
                        paths_section[ini_key] = value[1:]
                    else:
                        paths_section[ini_key] = value
            
            # Add run wait flags
            for i in range(1, 4):
                paths_section[f"PreLaunchApp{i}RunWait"] = '1' if game_data.get(f'pre{i}_run_wait', False) else '0'
                paths_section[f"PostLaunchApp{i}RunWait"] = '1' if game_data.get(f'post{i}_run_wait', False) else '0'
            
            paths_section["JustAfterLaunchAppRunWait"] = '1' if game_data.get('just_after_run_wait', False) else '0'
            paths_section["JustBeforeExitAppRunWait"] = '1' if game_data.get('just_before_run_wait', False) else '0'
            
            # Add sequences section
            sequences_section = config['Sequences']
            
            # Default launch sequence
            default_launch = ["Controller-Mapper", "Monitor-Config", "No-TB", "Pre1", "Pre2", "Pre3", "Borderless"]
            sequences_section['LaunchSequence'] = ','.join(default_launch)
            
            # Default exit sequence
            default_exit = ["Post1", "Post2", "Post3", "Monitor-Config", "Taskbar", "Controller-Mapper"]
            sequences_section['ExitSequence'] = ','.join(default_exit)
            
            # Create the Game.ini file path
            game_ini_path = os.path.join(profile_folder_path, "Game.ini")
            
            # Write the Game.ini file
            with open(game_ini_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            print(f"Created Game.ini at {game_ini_path}")
            return True
        except Exception as e:
            print(f"Error creating Game.ini: {str(e)}")
            return False
    
    def _process_path_columns(self, game_data, profile_folder_path, config):
        """Process path columns 8-20 according to the specified logic"""
        try:
            # Get the Game.ini file path
            game_ini_path = os.path.join(profile_folder_path, "Game.ini")
            
            # Read the existing Game.ini
            game_ini = configparser.ConfigParser()
            game_ini.optionxform = str  # Preserve case for keys
            game_ini.read(game_ini_path, encoding='utf-8')
            
            # Define the mapping of columns 8-20 to Game.ini keys
            column_mapping = {
                'p1_profile': 'Player1Profile',
                'p2_profile': 'Player2Profile',
                'desktop_ctrl': 'ControllerMapperApp',
                'game_monitor_cfg': 'MultiMonitorGamingConfig',
                'desktop_monitor_cfg': 'MultiMonitorMediaConfig',
                'post1': 'PostLaunchApp1',
                'post2': 'PostLaunchApp2',
                'post3': 'PostLaunchApp3',
                'pre1': 'PreLaunchApp1',
                'pre2': 'PreLaunchApp2',
                'pre3': 'PreLaunchApp3',
                'just_after': 'JustAfterLaunchApp',
                'just_before': 'JustBeforeExitApp'
            }
            
            # Define the mapping of ini keys to config.ini keys
            config_key_mapping = {
                'Player1Profile': 'player_1_profile_file',
                'Player2Profile': 'player_2_profile_file',
                'ControllerMapperApp': 'controller_mapper_app',
                'MultiMonitorGamingConfig': 'multimonitor_gaming_config_file',
                'MultiMonitorMediaConfig': 'multimonitor_media_desktop_config_file',
                'PostLaunchApp1': 'post_launch_app_1',
                'PostLaunchApp2': 'post_launch_app_2',
                'PostLaunchApp3': 'post_launch_app_3',
                'PreLaunchApp1': 'pre_launch_app_1',
                'PreLaunchApp2': 'pre_launch_app_2',
                'PreLaunchApp3': 'pre_launch_app_3',
                'JustAfterLaunchApp': 'just_after_launch_app',
                'JustBeforeExitApp': 'just_before_exit_app'
            }
            
            # Get the game name for path truncation
            game_name = game_data.get('name_override', '')
            
            # Ensure Paths section exists
            if 'Paths' not in game_ini:
                game_ini['Paths'] = {}
            
            # Process each column
            for column_key, ini_key in column_mapping.items():
                value = game_data.get(column_key, '')
                
                if not value:
                    continue
                
                # Check for path indicators
                if value.startswith('<'):
                    # Case 1 & 2: Column contains "<"
                    path = value[1:]  # Remove the "<" indicator
                    
                    if path:
                        # Case 1: Column contains a path with "<"
                        game_ini['Paths'][ini_key] = path
                    else:
                        # Case 2: Column contains "<" without a path
                        # Get absolute value from config.ini
                        config_key = config_key_mapping.get(ini_key)
                        if config and 'Element Locations' in config and config_key and config_key in config['Element Locations']:
                            default_value = config['Element Locations'][config_key]
                            game_ini['Paths'][ini_key] = default_value
                        else:
                            # If no default value is found, set to empty
                            game_ini['Paths'][ini_key] = ""
                
                elif value.startswith('>'):
                    # Case 3, 4, 5: Column contains ">"
                    path = value[1:]  # Remove the ">" indicator
                    
                    if path and os.path.exists(path):
                        # Case 3 & 4: Column contains a path with ">" and the file exists
                        # Check file size
                        file_size = os.path.getsize(path)
                        
                        if file_size <= self.max_file_size:  # 181KB
                            # Case 3: File size <= 181KB
                            # Copy file to profile folder and truncate path
                            try:
                                # Create destination path
                                dest_path = os.path.join(profile_folder_path, os.path.basename(path))
                                
                                # Copy the file
                                shutil.copy2(path, dest_path)
                                
                                # Truncate path to name override and write to Game.ini
                                truncated_path = os.path.join(game_name, os.path.basename(path))
                                game_ini['Paths'][ini_key] = truncated_path
                            except Exception:
                                # If copy fails, use absolute path
                                game_ini['Paths'][ini_key] = path
                        else:
                            # Case 4: File size > 181KB
                            # Write absolute path to Game.ini
                            game_ini['Paths'][ini_key] = path
                    else:
                        # Case 5: Column contains ">" but the file doesn't exist or no path
                        # Get default from config.ini
                        config_key = config_key_mapping.get(ini_key)
                        if config and 'Element Locations' in config and config_key and config_key in config['Element Locations']:
                            default_path = config['Element Locations'][config_key]
                            
                            if default_path and os.path.exists(default_path):
                                # Default file exists, check size
                                default_file_size = os.path.getsize(default_path)
                                
                                if default_file_size <= self.max_file_size:  # 181KB
                                    # Copy default file to profile folder and truncate path
                                    try:
                                        # Create destination path
                                        dest_path = os.path.join(profile_folder_path, os.path.basename(default_path))
                                        
                                        # Copy the file
                                        shutil.copy2(default_path, dest_path)
                                        
                                        # Truncate path to name override and write to Game.ini
                                        truncated_path = os.path.join(game_name, os.path.basename(default_path))
                                        game_ini['Paths'][ini_key] = truncated_path
                                    except Exception:
                                        # If copy fails, use absolute path
                                        game_ini['Paths'][ini_key] = default_path
                                else:
                                    # Default file too large
                                    game_ini['Paths'][ini_key] = default_path
                            else:
                                # Default file doesn't exist
                                game_ini['Paths'][ini_key] = default_path
                        else:
                            # If no default value is found, set to empty
                            game_ini['Paths'][ini_key] = ""
                else:
                    # No indicator, treat as absolute path
                    game_ini['Paths'][ini_key] = value
            
            # Write the updated Game.ini
            with open(game_ini_path, 'w', encoding='utf-8') as f:
                game_ini.write(f)
            
            return True
        except Exception as e:
            return False
    
    def _get_config(self):
        """Get configuration from config.ini"""
        try:
            config = configparser.ConfigParser()
            config_path = os.path.join(self.app_directory, "config.ini")
            
            if not os.path.exists(config_path):
                return None
            
            config.read(config_path, encoding='utf-8')
            return config
        except Exception as e:
            print(f"Error reading config: {str(e)}")
            return None
    
    def _fetch_additional_game_data(self, game_data, profile_folder_path):
        """Fetch additional game data from online sources"""
        try:
            # Only proceed if we have a valid game.ini file
            game_ini_path = os.path.join(profile_folder_path, "Game.ini")
            if not os.path.exists(game_ini_path):
                print(f"Game.ini not found at {game_ini_path}, skipping data fetch")
                return False
            
            # Process the path columns first to ensure < and > are properly handled
            path_processing_result = self._process_path_columns(game_data, profile_folder_path, self._get_config())
            if not path_processing_result:
                print(f"Failed to process path columns, skipping data fetch")
                return False
            
            # Now create the GameDataFetcher instance
            data_fetcher = GameDataFetcher(self.main_window)
            
            # Connect signals - use print for status updates to avoid UI issues
            data_fetcher.status_update.connect(lambda msg: print(f"GameDataFetcher: {msg}"))
            
            # Start the fetch process
            data_fetcher.fetch_game_data(game_data, profile_folder_path)
            
            return True
        except Exception as e:
            print(f"Error starting data fetch: {str(e)}")
            return False



