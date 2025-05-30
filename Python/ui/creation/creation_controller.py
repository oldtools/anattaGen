"""
Controls the creation process for game profiles and launchers
"""

import os
from PyQt6.QtWidgets import QCheckBox, QMessageBox, QProgressDialog
from PyQt6.QtCore import QCoreApplication, Qt

from .config_writer import ConfigWriter
from .profile_manager import ProfileManager
from .file_propagator import FilePropagator
from .shortcut_manager import ShortcutManager

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
    
    def create_all(self, games=None, create_overwrite_launcher=True, create_profile_folders=True, create_overwrite_joystick_profiles=False):
        """Create all selected games"""
        # Initialize statistics
        self.stats = {
            'profiles_created': 0,
            'configs_updated': 0,
            'files_propagated': 0,
            'game_shortcuts_created': 0,
            'launcher_shortcuts_created': 0,
            'joystick_profiles_created': 0,
            'joystick_profiles_updated': 0
        }
        
        # Get the list of games if not provided
        if games is None:
            games = self._get_included_games()
        
        # If no games are selected, show a message
        if not games:
            QMessageBox.warning(self.main_window, "No Games Selected", "Please select at least one game by checking the Include checkbox.")
            return self.stats
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Creating game profiles and launchers...", "Cancel", 0, len(games), self.main_window)
        progress_dialog.setWindowTitle("Creating Games")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        progress_dialog.show()
        
        # Process each game
        for i, game_data in enumerate(games):
            # Update progress dialog
            progress_dialog.setValue(i)
            progress_dialog.setLabelText(f"Processing {game_data['name_override']}...")
            
            # Check if the user cancelled
            if progress_dialog.wasCanceled():
                break
            
            # Process the game
            self._process_game(
                game_data, 
                create_overwrite_launcher,
                create_profile_folders,
                create_overwrite_joystick_profiles
            )
            
            # Process events to keep UI responsive
            QCoreApplication.processEvents()
        
        # Close progress dialog
        progress_dialog.setValue(len(games))
        progress_dialog.close()
        
        # Show a summary message
        self._show_summary()
        
        return self.stats
    
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
    
    def _process_game(self, game_data, create_overwrite_launcher, create_profile_folders, create_overwrite_joystick_profiles):
        """Process a single game"""
        # 1. Create/update Game.ini
        config_result = self.config_writer.process_game_config(
            game_data, 
            create_profile_folders
        )
        self.stats['configs_updated'] += 1 if config_result else 0
        
        # 2. Create profile folder if enabled
        profile_folder_path = None
        if create_profile_folders:
            profile_folder_path = self.profile_manager.get_profile_folder_path(game_data)
            profile_result = self.profile_manager.create_profile_folder(game_data)
            self.stats['profiles_created'] += 1 if profile_result else 0
        else:
            # Get the profile folder path even if we're not creating it
            profile_folder_path = self.profile_manager.get_profile_folder_path(game_data)
        
        # 3. Propagate assets to the profile folder
        if profile_folder_path and os.path.exists(profile_folder_path):
            propagated_count = self.file_propagator.propagate_files(
                game_data, 
                profile_folder_path
            )
            self.stats['files_propagated'] += propagated_count
        
        # 4. Create shortcuts if enabled
        if create_overwrite_launcher:
            # Get the launchers directory
            launchers_dir = self.main_window.launchers_dir_edit.text()
            if launchers_dir and os.path.isdir(launchers_dir):
                # Create game shortcut in profile folder
                if profile_folder_path and os.path.exists(profile_folder_path):
                    game_shortcut_result = self.shortcut_manager.create_game_shortcut(
                        game_data, 
                        profile_folder_path
                    )
                    self.stats['game_shortcuts_created'] += 1 if game_shortcut_result else 0
                
                # Create launcher shortcut in launchers directory
                launcher_shortcut_result = self.shortcut_manager.create_launcher_shortcut(
                    game_data, 
                    profile_folder_path,
                    launchers_dir
                )
                self.stats['launcher_shortcuts_created'] += 1 if launcher_shortcut_result else 0
        
        # 5. Create/update joystick profiles if enabled
        if create_overwrite_joystick_profiles and self.joystick_profile_manager:
            joystick_result = self.joystick_profile_manager.process_joystick_profiles(
                game_data,
                create_profile_folders,
                True  # Overwrite existing profiles
            )
            self.stats['joystick_profiles_created'] += joystick_result.get('created', 0)
            self.stats['joystick_profiles_updated'] += joystick_result.get('updated', 0)
    
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








