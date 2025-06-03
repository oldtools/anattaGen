"""
Handles writing configuration files for games
This functionality has been consolidated into creation_controller.py
"""

import os
import configparser
from PyQt6.QtCore import QCoreApplication

class ConfigWriter:
    """Handles writing configuration files for games"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
    
    def process_game_config(self, game_data, profile_folder_path, launch_sequence=None, exit_sequence=None):
        """
        Create or update the Game.ini configuration file
        This is a stub - functionality moved to CreationController._write_game_config
        """
        print("ConfigWriter.process_game_config is deprecated. Use CreationController._write_game_config instead.")
        
        # Get configuration from config.ini
        config = self._get_config()
        if not config:
            return {'created': False, 'updated': False}
        
        # Create a new config file
        game_config = configparser.ConfigParser()
        game_config.optionxform = str  # Preserve case for keys
        
        # Ensure all sections exist
        for section in ['Game', 'Paths', 'Options', 'PreLaunch', 'PostLaunch', 'Sequences']:
            game_config[section] = {}
        
        # Create the Game.ini file path
        game_ini_path = os.path.join(profile_folder_path, "Game.ini")
        game_ini_exists = os.path.exists(game_ini_path)
        
        # Write the Game.ini file
        try:
            with open(game_ini_path, 'w', encoding='utf-8') as f:
                game_config.write(f)
            return {'created': not game_ini_exists, 'updated': game_ini_exists}
        except Exception as e:
            print(f"Error writing Game.ini: {str(e)}")
            return {'created': False, 'updated': False}
    
    def _get_config(self):
        """Get configuration from config.ini"""
        try:
            config = configparser.ConfigParser()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            config_path = os.path.join(app_root_dir, "config.ini")
            
            if not os.path.exists(config_path):
                return None
            
            config.read(config_path, encoding='utf-8')
            return config
        except Exception as e:
            print(f"Error reading config: {str(e)}")
            return None

