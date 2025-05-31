"""
Controls the creation process for game profiles and launchers
"""

import os
import configparser
from PyQt6.QtWidgets import QCheckBox, QMessageBox, QProgressDialog
from PyQt6.QtCore import QCoreApplication, Qt

from .config_writer import ConfigWriter
from .profile_manager import ProfileManager
from .file_propagator import FilePropagator
from .shortcut_manager import ShortcutManager
from .launcher_creator import LauncherCreator

# Try to import JoystickProfileManager, but don't fail if it doesn't exist
try:
    from .joystick_profile_manager import JoystickProfileManager
except ImportError:
    # Create a dummy class that does nothing
    class JoystickProfileManager:
        def __init__(self, main_window):
            pass
        
        def process_joystick_profiles(self, *args, **kwargs):
            return {'created': 0, 'updated': 0}

class CreationController:
    """Controls the creation process for game profiles and launchers"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        self.config_writer = ConfigWriter(main_window)
        self.profile_manager = ProfileManager(main_window)
        self.file_propagator = FilePropagator(main_window)
        self.shortcut_manager = ShortcutManager(main_window)
        self.launcher_creator = LauncherCreator(main_window)
        self.joystick_profile_manager = JoystickProfileManager(main_window) if 'JoystickProfileManager' in globals() else None
        
        # Statistics for the creation process
        self.stats = {
            'profiles_created': 0,
            'configs_updated': 0,
            'files_propagated': 0,
            'game_shortcuts_created': 0,
            'launcher_shortcuts_created': 0,
            'joystick_profiles_created': 0,
            'joystick_profiles_updated': 0
        }
    
    def create_all(self, games, create_overwrite_launcher=True, create_profile_folders=True, 
                   create_overwrite_joystick_profiles=False, launch_sequence=None, exit_sequence=None):
        """Create all the necessary files for the selected games"""
        stats = {
            'launchers_created': 0,
            'launchers_updated': 0,
            'profile_folders_created': 0,
            'joystick_profiles_created': 0,
            'joystick_profiles_updated': 0
        }
        
        # Process each game
        for game_data in games:
            game_stats = self._process_game(
                game_data, 
                create_overwrite_launcher, 
                create_profile_folders, 
                create_overwrite_joystick_profiles,
                launch_sequence,
                exit_sequence
            )
            
            # Update the stats
            for key, value in game_stats.items():
                if key in stats:
                    stats[key] += value
        
        return stats
    
    def _get_included_games(self):
        """Get the list of games with Include checked"""
        games = []
        
        # Get the editor table
        editor_table = self.main_window.editor_table
        
        # Iterate through all rows
        for row in range(editor_table.rowCount()):
            # Check if the Include checkbox is checked
            include_widget = editor_table.cellWidget(row, 0)
            if include_widget:
                # Get the checkbox from the widget
                checkbox = include_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    # Get the game data
                    game_data = {
                        'executable': editor_table.item(row, 1).text() if editor_table.item(row, 1) else '',
                        'directory': editor_table.item(row, 2).text() if editor_table.item(row, 2) else '',
                        'steam_title': editor_table.item(row, 3).text() if editor_table.item(row, 3) else '',
                        'name_override': editor_table.item(row, 4).text() if editor_table.item(row, 4) else '',
                        'options': editor_table.item(row, 5).text() if editor_table.item(row, 5) else '',
                        'arguments': editor_table.item(row, 6).text() if editor_table.item(row, 6) else '',
                        'steam_id': editor_table.item(row, 7).text() if editor_table.item(row, 7) else '',
                        'as_admin': self.main_window.run_as_admin_checkbox.isChecked() if hasattr(self.main_window, 'run_as_admin_checkbox') else False,
                        'no_tb': self.main_window.hide_taskbar_checkbox.isChecked() if hasattr(self.main_window, 'hide_taskbar_checkbox') else False,
                    }
                    
                    # Add the game to the list
                    games.append(game_data)
        
        return games
    
    def _process_game(self, game_data, create_overwrite_launcher, create_profile_folders, 
                     create_overwrite_joystick_profiles, launch_sequence=None, exit_sequence=None):
        """Process a single game"""
        import configparser
        
        game_stats = {
            'launchers_created': 0,
            'launchers_updated': 0,
            'profile_folders_created': 0,
            'game_shortcuts_created': 0,
            'launcher_shortcuts_created': 0,
            'joystick_profiles_created': 0,
            'joystick_profiles_updated': 0
        }
        
        # Get configuration from config.ini
        config = self._get_config()
        if not config:
            print("Failed to load configuration")
            return game_stats
        
        # Get profiles directory from config
        profiles_dir = None
        if 'Element Locations' in config and 'profiles_directory' in config['Element Locations']:
            profiles_dir = config['Element Locations']['profiles_directory']
        
        if not profiles_dir or not os.path.isdir(profiles_dir):
            print(f"Profiles directory not found or invalid: {profiles_dir}")
            return game_stats
        
        # Get launcher directory from config
        launcher_dir = None
        if 'Element Locations' in config and 'launchers_directory' in config['Element Locations']:
            launcher_dir = config['Element Locations']['launchers_directory']
        
        if not launcher_dir or not os.path.isdir(launcher_dir):
            print(f"Launchers directory not found or invalid: {launcher_dir}")
            return game_stats
        
        # Get the game name
        game_name = game_data.get('name_override', '')
        if not game_name:
            print(f"Game name not found for {game_data.get('executable', 'unknown')}")
            return game_stats
        
        # Create the profile folder path
        profile_folder_path = os.path.join(profiles_dir, game_name)
        
        # Create the profile folder
        if create_profile_folders:
            os.makedirs(profile_folder_path, exist_ok=True)
            game_stats['profile_folders_created'] += 1
            
            # Create the game shortcut in the profile folder
            if self.shortcut_manager.create_game_shortcut(game_data, profile_folder_path):
                game_stats['game_shortcuts_created'] += 1
                print(f"Created game shortcut in profile folder: {os.path.join(profile_folder_path, game_data['name_override'] + '.lnk')}")
            
            # Write the config file with launch and exit sequences
            config_result = self.config_writer.process_game_config(
                game_data, 
                create_profile_folders,
                launch_sequence=launch_sequence,
                exit_sequence=exit_sequence
            )
        
        # Create the launcher
        if create_overwrite_launcher:
            # Create the launcher script
            launcher_result = self.launcher_creator.create_launcher(
                game_data, 
                launch_sequence=launch_sequence,
                exit_sequence=exit_sequence
            )
            
            if launcher_result.get('created', False):
                game_stats['launchers_created'] += 1
            elif launcher_result.get('updated', False):
                game_stats['launchers_updated'] += 1
            
            # Create the launcher shortcut
            if self.shortcut_manager.create_launcher_shortcut(game_data, profile_folder_path, launcher_dir):
                game_stats['launcher_shortcuts_created'] += 1
                print(f"Created launcher shortcut: {os.path.join(launcher_dir, game_data['name_override'] + '.lnk')}")
        
        # Create or update joystick profiles
        if create_overwrite_joystick_profiles and self.joystick_profile_manager:
            joystick_result = self.joystick_profile_manager.process_joystick_profiles(
                game_data, 
                create_profile_folders, 
                overwrite_existing=True
            )
            
            game_stats['joystick_profiles_created'] += joystick_result.get('created', 0)
            game_stats['joystick_profiles_updated'] += joystick_result.get('updated', 0)
        
        return game_stats
    
    def _get_config(self):
        """Get configuration from config.ini"""
        try:
            config = configparser.ConfigParser()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            config_path = os.path.join(app_root_dir, "config.ini")
            
            if not os.path.exists(config_path):
                print(f"Configuration file not found: {config_path}")
                return None
            
            config.read(config_path, encoding='utf-8')
            return config
        except Exception as e:
            print(f"Error reading configuration: {e}")
            return None
    
    def _show_summary(self):
        """Show a summary of the creation process"""
        message = f"Creation process completed:\n\n"
        message += f"Profiles created: {self.stats['profiles_created']}\n"
        message += f"Configs updated: {self.stats['configs_updated']}\n"
        message += f"Files propagated: {self.stats['files_propagated']}\n"
        message += f"Game shortcuts created: {self.stats['game_shortcuts_created']}\n"
        message += f"Launcher shortcuts created: {self.stats['launcher_shortcuts_created']}\n"
        
        if self.joystick_profile_manager:
            message += f"Joystick profiles created: {self.stats['joystick_profiles_created']}\n"
            message += f"Joystick profiles updated: {self.stats['joystick_profiles_updated']}\n"
        
        QMessageBox.information(self.main_window, "Creation Summary", message)
















