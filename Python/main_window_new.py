from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QStatusBar, 
    QMessageBox, QMenu, QFileDialog, QTableWidgetItem, QCheckBox,
    QProgressDialog, 
)
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QCursor
import os

# Import tab population functions
from Python.ui.setup_tab_ui import populate_setup_tab
from Python.ui.deployment_tab_ui import populate_deployment_tab
from Python.ui.editor_tab_ui import populate_editor_tab
from Python.ui.config_manager import load_initial_config
from Python.ui.creation.creation_controller import CreationController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize sets for indexing
        self.release_groups_set = set()
        self.folder_exclude_set = set()
        self.exclude_exe_set = set()
        self.demoted_set = set()
        self.found_executables_cache = set()
        
        # Initialize Steam caches
        self.steam_title_cache = {}
        self.normalized_steam_match_index = {}
        
        # Load sets from files
        self._load_set_files()
        
        self._setup_ui()
        load_initial_config(self)
        
        # Initialize Steam cache manager
        from Python.ui.steam_cache import SteamCacheManager
        self.steam_cache_manager = SteamCacheManager(self)
        
        # Load Steam cache
        self._load_steam_cache()

    def _load_steam_cache(self):
        """Load Steam cache from files"""
        # Load filtered Steam cache
        self.steam_cache_manager.load_filtered_steam_cache()
        
        # Load normalized Steam index
        self.steam_cache_manager.load_normalized_steam_index()
        
    def _setup_ui(self):
        self.setWindowTitle("Game Environment Manager")
        self.setGeometry(100, 100, 740, 240)  # Reduced from 950, 750 to 800, 600

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create all tab widgets first
        self.setup_tab = QWidget()
        self.deployment_tab = QWidget()
        self.editor_tab = QWidget()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.setup_tab, "Setup")
        self.tabs.addTab(self.deployment_tab, "Deployment")
        self.tabs.addTab(self.editor_tab, "Editor")
        
        # Populate the tabs in the correct order
        # Populate the setup tab first
        populate_setup_tab(self)
        
        # Then populate the deployment tab (which may depend on setup tab elements)
        populate_deployment_tab(self)
        
        # Finally populate the editor tab
        populate_editor_tab(self)

        # Add Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")
        
    def _add_new_app_dialog(self, line_edit):
        """Handle the 'Add New...' option in app selection dropdowns"""
        # This is a placeholder for the actual implementation
        # It will be called when the user selects 'Add New...' in a dropdown
        pass
        
    def _prompt_and_process_steam_json(self, file_path=None):
        """Prompt the user to select a Steam JSON file and process it"""
        from Python.ui.steam_processor import SteamProcessor
        
        # Create processor if needed
        if not hasattr(self, 'steam_processor'):
            self.steam_processor = SteamProcessor(self, self.steam_cache_manager)
        
        # Process Steam JSON
        if file_path:
            self.steam_processor.process_steam_json(file_path)
        else:
            self.steam_processor.prompt_and_process_steam_json()
        
    def _update_steam_json_cache(self):
        """Update the Steam JSON cache"""
        # This method should update the Steam JSON cache
        self.statusBar().showMessage("Updating Steam JSON cache...", 5000)
        # In a real implementation, this would call a function to update the cache
        
    def _locate_and_exclude_manager_config(self):
        """Locate and exclude games from other managers' configurations"""
        from Python.ui.steam_utils import locate_and_exclude_manager_config
        locate_and_exclude_manager_config(self)
        
    def _get_editor_table_data(self):
        """Get the data from the editor table"""
        data = []
        
        # Iterate through all rows in the table
        for row in range(self.editor_table.rowCount()):
            row_data = {}
            
            # Get include checkbox state (column 0)
            include_widget = self.editor_table.cellWidget(row, 0)
            if include_widget and hasattr(include_widget, 'findChild'):
                checkbox = include_widget.findChild(QCheckBox)
                if checkbox:
                    row_data["include"] = checkbox.isChecked()
                else:
                    row_data["include"] = False
            else:
                row_data["include"] = False
            
            # Get text from columns 1-7
            row_data["executable"] = self.editor_table.item(row, 1).text() if self.editor_table.item(row, 1) else ""
            row_data["directory"] = self.editor_table.item(row, 2).text() if self.editor_table.item(row, 2) else ""
            row_data["steam_title"] = self.editor_table.item(row, 3).text() if self.editor_table.item(row, 3) else ""
            row_data["name_override"] = self.editor_table.item(row, 4).text() if self.editor_table.item(row, 4) else ""
            row_data["options"] = self.editor_table.item(row, 5).text() if self.editor_table.item(row, 5) else ""
            row_data["arguments"] = self.editor_table.item(row, 6).text() if self.editor_table.item(row, 6) else ""
            row_data["steam_id"] = self.editor_table.item(row, 7).text() if self.editor_table.item(row, 7) else ""
            
            # Get path indicators from columns 8-20
            path_indicators = {}
            for col in range(8, 21):
                indicator = self.editor_table.item(row, col).text() if self.editor_table.item(row, col) else "<"
                path_indicators[f"col_{col}_indicator"] = indicator
            
            row_data["path_indicators"] = path_indicators
            
            # Get borderless status from column 21
            row_data["borderless"] = self.editor_table.item(row, 21).text() if self.editor_table.item(row, 21) else ""
            
            # Get as_admin and no_tb from columns 22-23
            as_admin_widget = self.editor_table.cellWidget(row, 22)
            if as_admin_widget and hasattr(as_admin_widget, 'findChild'):
                checkbox = as_admin_widget.findChild(QCheckBox)
                if checkbox:
                    row_data["as_admin"] = checkbox.isChecked()
                else:
                    row_data["as_admin"] = False
            else:
                row_data["as_admin"] = False
            
            no_tb_widget = self.editor_table.cellWidget(row, 23)
            if no_tb_widget and hasattr(no_tb_widget, 'findChild'):
                checkbox = no_tb_widget.findChild(QCheckBox)
                if checkbox:
                    row_data["no_tb"] = checkbox.isChecked()
                else:
                    row_data["no_tb"] = False
            else:
                row_data["no_tb"] = False
            
            data.append(row_data)
        
        return data
        
    def _index_sources(self):
        """Index the source directories"""
        from Python.ui.game_indexer import index_games
        
        # Get the name check option
        enable_name_matching = False
        if hasattr(self, 'name_check_checkbox'):
            enable_name_matching = self.name_check_checkbox.isChecked()
        
        # Call the indexing function with the name matching option
        self.statusBar().showMessage("Indexing source directories...", 0)
        count = index_games(self, enable_name_matching=enable_name_matching)
        self.statusBar().showMessage(f"Indexed {count} executables", 5000)
        
    def _load_index(self):
        """Load index file into editor table"""
        from Python.ui.index_manager import load_index
        data = load_index(self)
        
        # Clear the existing table
        self.editor_table.setRowCount(0)
        
        # Populate the table with the loaded data
        for row_data in data:
            # Get current row count
            row = self.editor_table.rowCount()
            self.editor_table.insertRow(row)
            
            # Create include checkbox
            from Python.ui.game_indexer import create_status_widget
            include_widget = create_status_widget(self, row_data.get("include", False), row, 0)
            self.editor_table.setCellWidget(row, 0, include_widget)
            
            # Set text items
            self.editor_table.setItem(row, 1, QTableWidgetItem(row_data.get("executable", "")))
            self.editor_table.setItem(row, 2, QTableWidgetItem(row_data.get("directory", "")))
            self.editor_table.setItem(row, 3, QTableWidgetItem(row_data.get("steam_title", "")))
            self.editor_table.setItem(row, 4, QTableWidgetItem(row_data.get("name_override", "")))
            self.editor_table.setItem(row, 5, QTableWidgetItem(row_data.get("options", "")))
            self.editor_table.setItem(row, 6, QTableWidgetItem(row_data.get("arguments", "")))
            self.editor_table.setItem(row, 7, QTableWidgetItem(row_data.get("steam_id", "")))
            
            # Set path fields with their indicators
            path_indicators = row_data.get("path_indicators", {})
            
            # Set path fields (columns 8-20)
            path_fields = [
                "p1_profile", "p2_profile", "desktop_ctrl", 
                "game_monitor_cfg", "desktop_monitor_cfg", 
                "post1", "post2", "post3", 
                "pre1", "pre2", "pre3", 
                "just_after", "just_before"
            ]
            
            for i, field in enumerate(path_fields):
                col = i + 8
                # Check if we have a stored indicator
                indicator = path_indicators.get(f"col_{col}_indicator", "<")  # Default to CEN
                # If no indicator in path_indicators, use the value from the field
                if f"col_{col}_indicator" not in path_indicators and field in row_data:
                    indicator = row_data[field]
                # If still no indicator, default to CEN
                if not indicator:
                    indicator = "<"
                self.editor_table.setItem(row, col, QTableWidgetItem(indicator))
            
            # Set borderless status
            self.editor_table.setItem(row, 21, QTableWidgetItem(row_data.get("borderless", "")))
            
            # Set as_admin and no_tb checkboxes
            as_admin_widget = create_status_widget(self, row_data.get("as_admin", False), row, 22)
            self.editor_table.setCellWidget(row, 22, as_admin_widget)
            
            no_tb_widget = create_status_widget(self, row_data.get("no_tb", False), row, 23)
            self.editor_table.setCellWidget(row, 23, no_tb_widget)
        
        self.statusBar().showMessage(f"Loaded {len(data)} entries", 3000)
        
    def _save_editor_table_to_index(self):
        """Save the editor table data to the index file"""
        from Python.ui.index_manager import save_index
        
        # Get the data from the editor table
        data = self._get_editor_table_data()
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(script_dir)
        
        # Save the data to the index file
        save_index(self, app_root_dir, data)
        
        self.statusBar().showMessage("Index saved", 3000)
        
    def _on_delete_indexes(self):
        """Delete index files"""
        # This is a placeholder for the actual implementation
        # It will be called when the user clicks "Delete Indexes" in the editor tab
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText("Are you sure you want to delete all index files?")
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            # Delete index files
            from Python.ui.index_manager import delete_indexes
            delete_indexes(self)
            self.statusBar().showMessage("Index files deleted", 3000)
        
    def _on_clear_listview(self):
        """Clear the editor table"""
        # This is a placeholder for the actual implementation
        # It will be called when the user clicks "Clear List-View" in the editor tab
        self.editor_table.setRowCount(0)
        self.statusBar().showMessage("List view cleared", 3000)
        
    def _regenerate_all_names(self):
        """Regenerate all name overrides in the table"""
        # This is a placeholder for the actual implementation
        # It will be called when the user clicks "Regenerate All Names" in the editor tab
        from Python.ui.name_processor import regenerate_all_names
        regenerate_all_names(self)
        self.statusBar().showMessage("All names regenerated", 3000)
        
    def _on_editor_table_cell_left_click(self, row, column):
        """Handle left-click on a cell in the editor table"""
        # This is a placeholder for the actual implementation
        # It will be called when the user left-clicks on a cell in the editor table
        pass
        
    def _on_editor_table_custom_context_menu(self, position):
        """Handle right-click on the editor table"""
        # This is a placeholder for the actual implementation
        # It will be called when the user right-clicks on the editor table
        context_menu = QMenu(self)
        
        # Add actions to the menu
        edit_action = context_menu.addAction("Edit")
        copy_action = context_menu.addAction("Copy")
        paste_action = context_menu.addAction("Paste")
        delete_action = context_menu.addAction("Delete")
        
        # Show the menu at the cursor position
        action = context_menu.exec(QCursor.pos())
        
        # Handle the selected action
        if action == edit_action:
            # Edit the selected row
            pass
        elif action == delete_action:
            # Delete the selected row
            pass
        
        if action == copy_action:
            # Copy the selected row
            pass
        
        if action == paste_action:
            # Paste the selected row
            pass
        
        
    def _on_editor_table_header_click(self, column):
        """Handle click on a header in the editor table"""
        # This is a placeholder for the actual implementation
        # It will be called when the user clicks on a header in the editor table
        pass
        
    def _on_editor_table_edited(self, item):
        """Handle editing of a cell in the editor table"""
        # This is a placeholder for the actual implementation
        # It will be called when a cell in the editor table is edited
        pass

    def _load_set_files(self):
        """Load set files into memory"""
        from Python.ui.game_indexer import load_set_file
        
        # Load release groups
        self.release_groups_set = load_set_file("Python/release_groups.set")
        
        # Load folder exclusions
        self.folder_exclude_set = load_set_file("Python/folder_exclude.set")
        
        # Load executable exclusions
        self.exclude_exe_set = load_set_file("Python/exclude_exe.set")
        
        # Load demoted items
        self.demoted_set = load_set_file("Python/demoted.set")

    def _setup_creation_controller(self):
        """Initialize the creation controller"""
        self.creation_controller = CreationController(self)

    def _create_selected_games(self):
        """Create launchers and profiles for selected games"""
        # Make sure the creation controller is initialized
        if not hasattr(self, 'creation_controller'):
            self._setup_creation_controller()
        
        # Get the data from the editor table
        selected_games = []
        
        # Iterate through all rows in the editor table
        for row in range(self.editor_table.rowCount()):
            # Check if the Include checkbox is checked
            include_widget = self.editor_table.cellWidget(row, 0)
            if include_widget:
                # Get the checkbox from the widget
                checkbox = include_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    # Get the game data
                    game_data = {
                        'executable': self.editor_table.item(row, 1).text() if self.editor_table.item(row, 1) else '',
                        'directory': self.editor_table.item(row, 2).text() if self.editor_table.item(row, 2) else '',
                        'steam_title': self.editor_table.item(row, 3).text() if self.editor_table.item(row, 3) else '',
                        'name_override': self.editor_table.item(row, 4).text() if self.editor_table.item(row, 4) else '',
                        'options': self.editor_table.item(row, 5).text() if self.editor_table.item(row, 5) else '',
                        'arguments': self.editor_table.item(row, 6).text() if self.editor_table.item(row, 6) else '',
                        'steam_id': self.editor_table.item(row, 7).text() if self.editor_table.item(row, 7) else '',
                        'as_admin': self.run_as_admin_checkbox.isChecked() if hasattr(self, 'run_as_admin_checkbox') else False,
                        'no_tb': self.hide_taskbar_checkbox.isChecked() if hasattr(self, 'hide_taskbar_checkbox') else False,
                    }
                    
                    # Add the game to the list
                    selected_games.append(game_data)
        
        # If no games are selected, show a message
        if not selected_games:
            QMessageBox.warning(self, "No Games Selected", "Please select at least one game by checking the Include checkbox.")
            return
        
        # Start the creation process with the selected games
        from Python.ui.creation.creation_controller import CreationController
        creation_controller = CreationController(self)
        
        # Get creation options from UI
        create_overwrite_launcher = True
        create_profile_folders = True
        create_overwrite_joystick_profiles = False
        
        if hasattr(self, 'create_overwrite_launcher_checkbox'):
            create_overwrite_launcher = self.create_overwrite_launcher_checkbox.isChecked()
        
        if hasattr(self, 'create_profile_folders_checkbox'):
            create_profile_folders = self.create_profile_folders_checkbox.isChecked()
        
        if hasattr(self, 'create_overwrite_joystick_profiles_checkbox'):
            create_overwrite_joystick_profiles = self.create_overwrite_joystick_profiles_checkbox.isChecked()
        
        # Call create_all with the selected games and options
        stats = creation_controller.create_all(
            selected_games,
            create_overwrite_launcher,
            create_profile_folders,
            create_overwrite_joystick_profiles
        )
        
        # Show a summary message
        summary = f"Creation process completed:\n\n"
        summary += f"- Profiles created: {stats['profiles_created']}\n"
        summary += f"- Configs updated: {stats['configs_updated']}\n"
        summary += f"- Files propagated: {stats['files_propagated']}\n"
        summary += f"- Game shortcuts created: {stats['game_shortcuts_created']}\n"
        summary += f"- Launcher shortcuts created: {stats['launcher_shortcuts_created']}\n"
        
        if 'joystick_profiles_created' in stats and stats['joystick_profiles_created'] > 0:
            summary += f"- Joystick profiles created: {stats['joystick_profiles_created']}\n"
        
        if 'joystick_profiles_updated' in stats and stats['joystick_profiles_updated'] > 0:
            summary += f"- Joystick profiles updated: {stats['joystick_profiles_updated']}\n"
        
        QMessageBox.information(self, "Creation Complete", summary)

    def _save_config_on_radio_change(self, checked, key):
        """Save configuration when a radio button is toggled"""
        if checked:
            # Only save when a button is checked (not when unchecked)
            from Python.ui.config_manager import save_configuration
            print(f"Radio button toggled for {key}, saving configuration...")
            save_configuration(self)
            print(f"Configuration saved after radio button toggle for {key}")

    def _on_create_button_clicked(self):
        """Handle the Create button click"""
        # Get the selected games
        selected_games = self._get_selected_games_from_editor()
        if not selected_games:
            QMessageBox.warning(self, "No Games Selected", "Please select at least one game to create files for.")
            return
        
        # Get the creation options
        create_overwrite_launcher = True
        create_profile_folders = True
        create_overwrite_joystick_profiles = False
        
        if hasattr(self, 'create_overwrite_launcher_checkbox'):
            create_overwrite_launcher = self.create_overwrite_launcher_checkbox.isChecked()
        
        if hasattr(self, 'create_profile_folders_checkbox'):
            create_profile_folders = self.create_profile_folders_checkbox.isChecked()
        
        if hasattr(self, 'create_overwrite_joystick_profiles_checkbox'):
            create_overwrite_joystick_profiles = self.create_overwrite_joystick_profiles_checkbox.isChecked()
        
        # Get the launch and exit sequences from the reordering lists
        launch_sequence = []
        exit_sequence = []
        
        if hasattr(self, 'launch_sequence_list'):
            launch_sequence = [self.launch_sequence_list.item(i).text() for i in range(self.launch_sequence_list.count())]
        
        if hasattr(self, 'exit_sequence_list'):
            exit_sequence = [self.exit_sequence_list.item(i).text() for i in range(self.exit_sequence_list.count())]
        
        # Save the sequences to config.ini
        from Python.ui.config_manager import save_launch_exit_sequences
        save_launch_exit_sequences(self, launch_sequence, exit_sequence)
        
        # Create the creation controller
        from Python.ui.creation.creation_controller import CreationController
        creation_controller = CreationController(self)
        
        # Create the files
        stats = creation_controller.create_all(
            selected_games,
            create_overwrite_launcher,
            create_profile_folders,
            create_overwrite_joystick_profiles,
            launch_sequence,
            exit_sequence
        )
        
        # Show the results
        message = f"Creation complete!\n\n"
        message += f"Launchers created: {stats['launchers_created']}\n"
        message += f"Launchers updated: {stats['launchers_updated']}\n"
        message += f"Profile folders created: {stats['profile_folders_created']}\n"
        message += f"Joystick profiles created: {stats['joystick_profiles_created']}\n"
        message += f"Joystick profiles updated: {stats['joystick_profiles_updated']}\n"
        
        QMessageBox.information(self, "Creation Complete", message)

    def _get_selected_games_from_editor(self):
        """Get the selected games from the editor table"""
        selected_games = []
        
        # Iterate through all rows in the editor table
        for row in range(self.editor_table.rowCount()):
            # Check if the Include checkbox is checked
            include_widget = self.editor_table.cellWidget(row, 0)
            if include_widget:
                # Get the checkbox from the widget
                checkbox = include_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    # Get the game data
                    game_data = {
                        'executable': self.editor_table.item(row, 1).text() if self.editor_table.item(row, 1) else '',
                        'directory': self.editor_table.item(row, 2).text() if self.editor_table.item(row, 2) else '',
                        'steam_title': self.editor_table.item(row, 3).text() if self.editor_table.item(row, 3) else '',
                        'name_override': self.editor_table.item(row, 4).text() if self.editor_table.item(row, 4) else '',
                        'options': self.editor_table.item(row, 5).text() if self.editor_table.item(row, 5) else '',
                        'arguments': self.editor_table.item(row, 6).text() if self.editor_table.item(row, 6) else '',
                        'steam_id': self.editor_table.item(row, 7).text() if self.editor_table.item(row, 7) else '',
                        'as_admin': self.run_as_admin_checkbox.isChecked() if hasattr(self, 'run_as_admin_checkbox') else False,
                        'no_tb': self.hide_taskbar_checkbox.isChecked() if hasattr(self, 'hide_taskbar_checkbox') else False,
                    }
                    
                    # Add the game to the list
                    selected_games.append(game_data)
        
        return selected_games

    def _download_steam_json(self, version=2):
        """Download the Steam JSON file"""
        import urllib.request
        import os
        import shutil
        from PyQt6.QtWidgets import QMessageBox
        
        # Get the URL from the repos.set file
        url = None
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            repos_file = os.path.join(script_dir, "repos.set")
            
            if os.path.exists(repos_file):
                with open(repos_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if version == 1 and "STEAMJSON1" in line:
                            url = line.split("=")[1].strip()
                            break
                        elif version == 2 and "STEAMJSON2" in line:
                            url = line.split("=")[1].strip()
                            break
        except Exception as e:
            print(f"Error reading repos.set file: {e}")
        
        if not url:
            # Use default URLs if not found in repos.set
            if version == 1:
                url = "http://api.steampowered.com/ISteamApps/GetAppList/v1/?format=json"
            else:
                url = "http://api.steampowered.com/ISteamApps/GetAppList/v2/?format=json"
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(script_dir)
        
        # Create the output file path
        output_file = os.path.join(app_root_dir, "steam.json")
        
        # If the file already exists, back it up
        if os.path.exists(output_file):
            backup_file = os.path.join(app_root_dir, "steam.json.old")
            try:
                # Remove old backup if it exists
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                
                # Create backup
                shutil.copy2(output_file, backup_file)
                print(f"Backed up existing steam.json to {backup_file}")
            except Exception as e:
                print(f"Error backing up steam.json: {e}")
        
        # Show a message to the user
        self.statusBar().showMessage(f"Downloading Steam JSON (v{version})...", 0)
        
        try:
            # Download the file
            urllib.request.urlretrieve(url, output_file)
            
            # Check if the file was downloaded successfully
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                self.statusBar().showMessage(f"Steam JSON (v{version}) downloaded successfully", 5000)
                
                # Ask if the user wants to process the file now
                reply = QMessageBox.question(
                    self, 
                    "Process Steam JSON", 
                    "Steam JSON downloaded successfully. Do you want to process it now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Backup existing cache files before processing
                    self._backup_steam_cache_files()
                    
                    # Process the file
                    self._prompt_and_process_steam_json(output_file)
            else:
                self.statusBar().showMessage(f"Failed to download Steam JSON (v{version})", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Error downloading Steam JSON: {str(e)}", 5000)
            print(f"Error downloading Steam JSON: {e}")

    def _backup_steam_cache_files(self):
        """Backup Steam cache files before processing"""
        import os
        import shutil
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(script_dir)
        
        # Get the cache file paths
        from Python.ui.steam_cache import STEAM_FILTERED_TXT, NORMALIZED_INDEX_CACHE
        filtered_cache_path = os.path.join(app_root_dir, STEAM_FILTERED_TXT)
        normalized_index_path = os.path.join(app_root_dir, NORMALIZED_INDEX_CACHE)
        
        # Backup filtered cache if it exists
        if os.path.exists(filtered_cache_path):
            backup_path = filtered_cache_path + ".old"
            try:
                # Remove old backup if it exists
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                
                # Create backup
                shutil.copy2(filtered_cache_path, backup_path)
                print(f"Backed up {STEAM_FILTERED_TXT} to {backup_path}")
            except Exception as e:
                print(f"Error backing up {STEAM_FILTERED_TXT}: {e}")
        
        # Backup normalized index if it exists
        if os.path.exists(normalized_index_path):
            backup_path = normalized_index_path + ".old"
            try:
                # Remove old backup if it exists
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                
                # Create backup
                shutil.copy2(normalized_index_path, backup_path)
                print(f"Backed up {NORMALIZED_INDEX_CACHE} to {backup_path}")
            except Exception as e:
                print(f"Error backing up {NORMALIZED_INDEX_CACHE}: {e}")

    def _prompt_and_process_steam_json(self, file_path=None):
        """Prompt the user to select a Steam JSON file and process it"""
        from Python.ui.steam_processor import SteamProcessor
        
        # Create processor if needed
        if not hasattr(self, 'steam_processor'):
            self.steam_processor = SteamProcessor(self, self.steam_cache_manager)
        
        # Process Steam JSON
        if file_path:
            self.steam_processor.process_steam_json_file(file_path)
        else:
            self.steam_processor.prompt_and_process_steam_json()

    def _delete_steam_cache(self):
        """Delete the Steam cache files"""
        import os
        from PyQt6.QtWidgets import QMessageBox
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(script_dir)
        
        # Get the cache file paths
        from Python.ui.steam_cache import STEAM_FILTERED_TXT, NORMALIZED_INDEX_CACHE
        filtered_cache_path = os.path.join(app_root_dir, STEAM_FILTERED_TXT)
        normalized_index_path = os.path.join(app_root_dir, NORMALIZED_INDEX_CACHE)
        
        # Ask for confirmation
        reply = QMessageBox.question(
            self, 
            "Delete Steam Cache", 
            "Are you sure you want to delete the Steam cache files?\n\n"
            f"This will delete:\n- {STEAM_FILTERED_TXT}\n- {NORMALIZED_INDEX_CACHE}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete the files
            files_deleted = 0
            
            if os.path.exists(filtered_cache_path):
                try:
                    os.remove(filtered_cache_path)
                    files_deleted += 1
                    print(f"Deleted {filtered_cache_path}")
                except Exception as e:
                    print(f"Error deleting {filtered_cache_path}: {e}")
            
            if os.path.exists(normalized_index_path):
                try:
                    os.remove(normalized_index_path)
                    files_deleted += 1
                    print(f"Deleted {normalized_index_path}")
                except Exception as e:
                    print(f"Error deleting {normalized_index_path}: {e}")
            
            # Reset the cache in memory
            if hasattr(self, 'steam_cache_manager'):
                self.steam_cache_manager.reset_steam_caches()
            
            # Show a message
            self.statusBar().showMessage(f"Deleted {files_deleted} Steam cache files", 5000)

    def _delete_steam_json(self):
        """Delete the Steam JSON file"""
        import os
        from PyQt6.QtWidgets import QMessageBox
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(script_dir)
        
        # Get the JSON file path
        json_file_path = os.path.join(app_root_dir, "steam.json")
        
        # Ask for confirmation
        reply = QMessageBox.question(
            self, 
            "Delete Steam JSON", 
            "Are you sure you want to delete the Steam JSON file?\n\n"
            "This will delete:\n- steam.json",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete the file
            if os.path.exists(json_file_path):
                try:
                    os.remove(json_file_path)
                    print(f"Deleted {json_file_path}")
                    self.statusBar().showMessage("Steam JSON file deleted", 5000)
                except Exception as e:
                    self.statusBar().showMessage(f"Error deleting Steam JSON: {str(e)}", 5000)
                    print(f"Error deleting {json_file_path}: {e}")
            else:
                self.statusBar().showMessage("Steam JSON file not found", 5000)
