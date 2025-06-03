from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QStatusBar, 
    QMessageBox, QMenu, QFileDialog, QTableWidgetItem, QCheckBox,
    QProgressDialog, QVBoxLayout, QHBoxLayout, QHeaderView
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
        """Initialize the main window"""
        super().__init__()
        
        # Initialize member variables
        self.source_dirs = []
        self.release_groups_set = set()
        self.folder_exclude_set = set()
        self.exclude_exe_set = set()
        self.demoted_set = set()
        self.folder_demoted_set = set()
        
        # Set up the UI
        self._setup_ui()
        
        # Load set files
        self._load_set_files()
        
        # Initialize the creation controller
        self._setup_creation_controller()
        
        # Show the window
        self.show()

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
        
        # Load configuration AFTER UI elements are created
        from Python.ui.config_manager import load_initial_config
        load_initial_config(self)
        
        # Create status bar
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
        """Index the source directories and save to current.index with automatic backup"""
        from Python.ui.game_indexer import index_games
        from Python.ui.index_manager import save_index, backup_index
        
        # Get the name check option
        enable_name_matching = False
        if hasattr(self, 'name_check_checkbox'):
            enable_name_matching = self.name_check_checkbox.isChecked()
        
        # Call the indexing function with the name matching option
        self.statusBar().showMessage("Indexing source directories...", 0)
        count = index_games(self, enable_name_matching=enable_name_matching)
        
        # Save the indexed data to current.index (without prompt)
        if count > 0:
            # Get the data from the editor table
            data = self._get_editor_table_data()
            
            # Get the app's root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(script_dir)
            
            # Save the data to current.index (without prompt)
            # This will automatically create a backup in index_backups
            save_index(self, app_root_dir, data)
        
        self.statusBar().showMessage(f"Indexed {count} executables", 5000)
        return count
        
    def _load_index(self):
        """Load index file into editor table by prompting for a file"""
        from Python.ui.index_manager import load_index
        import traceback
        
        try:
            # Get the app's root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(script_dir)
            
            # Load the index data with file prompt
            print("Calling load_index function with prompt...")
            data = load_index(self, app_root_dir, prompt_for_filename=True)
            
            # If no data was loaded (user cancelled or error), return
            if not data:
                return False
            
            print(f"Loaded {len(data)} entries from index")
            
            # Clear the existing table
            print("Clearing editor table...")
            self.editor_table.setRowCount(0)
            
            # Disable table signals temporarily to prevent excessive updates
            print("Disabling table signals...")
            self.editor_table.blockSignals(True)
            
            # Populate the table with the loaded data
            print("Populating table with data...")
            from Python.ui.game_indexer import create_status_widget
            
            # Set row count at once to avoid multiple resize events
            self.editor_table.setRowCount(len(data))
            
            for row_index, row_data in enumerate(data):
                try:
                    # Create a checkbox for the Include column
                    include_checkbox_widget = create_status_widget(self, row_data.get("include", False), row_index, 0)
                    self.editor_table.setCellWidget(row_index, 0, include_checkbox_widget)
                    
                    # Set the items in the table
                    self.editor_table.setItem(row_index, 1, QTableWidgetItem(str(row_data.get("executable", ""))))
                    self.editor_table.setItem(row_index, 2, QTableWidgetItem(str(row_data.get("directory", ""))))
                    self.editor_table.setItem(row_index, 3, QTableWidgetItem(str(row_data.get("steam_title", ""))))
                    self.editor_table.setItem(row_index, 4, QTableWidgetItem(str(row_data.get("name_override", ""))))
                    self.editor_table.setItem(row_index, 5, QTableWidgetItem(str(row_data.get("options", ""))))
                    self.editor_table.setItem(row_index, 6, QTableWidgetItem(str(row_data.get("arguments", ""))))
                    self.editor_table.setItem(row_index, 7, QTableWidgetItem(str(row_data.get("steam_id", ""))))
                    
                    # Set path fields with their indicators
                    path_indicators = row_data.get("path_indicators", {})
                    path_fields = [
                        "p1_profile", "p2_profile", "desktop_ctrl", 
                        "game_monitor_cfg", "desktop_monitor_cfg", 
                        "post1", "post2", "post3", 
                        "pre1", "pre2", "pre3", 
                        "just_after", "just_before"
                    ]
                    
                    for i, field in enumerate(path_fields, 8):
                        indicator = path_indicators.get(f"col_{i}_indicator", "<")
                        value = str(row_data.get(field, ""))
                        # If indicator is in the value, use it directly
                        if value and (value.startswith('<') or value.startswith('>')):
                            self.editor_table.setItem(row_index, i, QTableWidgetItem(value))
                        else:
                            # Otherwise, use the indicator from path_indicators
                            self.editor_table.setItem(row_index, i, QTableWidgetItem(indicator + value))
                    
                    # Set borderless value
                    self.editor_table.setItem(row_index, 21, QTableWidgetItem(str(row_data.get("borderless", "No"))))
                    
                    # Create checkboxes for as_admin and no_tb
                    as_admin_checkbox_widget = create_status_widget(self, row_data.get("as_admin", False), row_index, 22)
                    self.editor_table.setCellWidget(row_index, 22, as_admin_checkbox_widget)
                    
                    no_tb_checkbox_widget = create_status_widget(self, row_data.get("no_tb", False), row_index, 23)
                    self.editor_table.setCellWidget(row_index, 23, no_tb_checkbox_widget)
                except Exception as e:
                    print(f"Error processing row {row_index}: {str(e)}")
                    traceback.print_exc()
                    # Continue with the next row instead of failing completely
                    continue
            
            # Re-enable table signals
            print("Re-enabling table signals...")
            self.editor_table.blockSignals(False)
            
            # Process events to ensure UI updates
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            
            print("Index loading complete")
            return True
        except Exception as e:
            print(f"Error in _load_index: {str(e)}")
            traceback.print_exc()
            self.statusBar().showMessage(f"Error loading index: {str(e)}", 3000)
            return False
        
    def _save_editor_table_to_index(self):
        """Save the editor table data to an index file with prompt"""
        from Python.ui.index_manager import save_index
        
        # Get the data from the editor table
        data = self._get_editor_table_data()
        
        # Get the app's root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(script_dir)
        
        # Save the data to the index file with prompt
        saved_path = save_index(self, app_root_dir, data)
        
        if saved_path:
            self.statusBar().showMessage(f"Index saved to {saved_path}", 3000)
            return True
        else:
            # User cancelled or error occurred
            return False
        
    def _on_delete_indexes(self):
        """Delete index files with confirmation"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText("Are you sure you want to delete all index files?")
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            # Delete index files
            from Python.ui.index_manager import delete_all_indexes
            
            # Get the app's root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(script_dir)
            
            delete_all_indexes(app_root_dir)
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
        """Called when the editor table is edited"""
        # Save the editor table data to the index file
        self._save_editor_table_to_index()
        
        # Update the status bar
        self.statusBar().showMessage("Editor table updated and saved", 3000)

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
        
        # Load additional items for demoting folders by name
        self.folder_demoted_set = load_set_file("Python/folder_demoted.set")

    def _setup_creation_controller(self):
        """Initialize the creation controller"""
        from Python.ui.creation.creation_controller import CreationController
        self.creation_controller = CreationController(self)

    def _create_selected_games(self):
        """Create launchers and profiles for selected games"""
        # Make sure the creation controller is initialized
        if not hasattr(self, 'creation_controller'):
            from Python.ui.creation.creation_controller import CreationController
            self.creation_controller = CreationController(self)
        
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
                    # Extract all data from the row
                    game_data = self._extract_game_data_from_row(row)
                    
                    # Add the game to the list
                    selected_games.append(game_data)
        
        # If no games are selected, show a message
        if not selected_games:
            QMessageBox.warning(self, "No Games Selected", "Please select at least one game by checking the Include checkbox.")
            return
        
        # Call create_all with the selected games
        result = self.creation_controller.create_all(selected_games)
        
        # Show a summary message
        if result['failed_count'] > 0:
            QMessageBox.warning(self, "Creation Complete", f"{result['failed_count']} games failed to process.")
        else:
            QMessageBox.information(self, "Creation Complete", "All selected games processed successfully.")

    def _extract_game_data_from_row(self, row):
        """Extract all game data from a table row"""
        # Create a dictionary to store the game data
        game_data = {}
        
        # Get checkbox values
        def get_checkbox_value(row, col):
            widget = self.editor_table.cellWidget(row, col)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox:
                    return checkbox.isChecked()
            return False
        
        # Get basic fields
        game_data['include'] = get_checkbox_value(row, 0)
        game_data['executable'] = self.editor_table.item(row, 1).text() if self.editor_table.item(row, 1) else ""
        game_data['directory'] = self.editor_table.item(row, 2).text() if self.editor_table.item(row, 2) else ""
        game_data['steam_title'] = self.editor_table.item(row, 3).text() if self.editor_table.item(row, 3) else ""
        game_data['name_override'] = self.editor_table.item(row, 4).text() if self.editor_table.item(row, 4) else ""
        game_data['options'] = self.editor_table.item(row, 5).text() if self.editor_table.item(row, 5) else ""
        game_data['arguments'] = self.editor_table.item(row, 6).text() if self.editor_table.item(row, 6) else ""
        game_data['steam_id'] = self.editor_table.item(row, 7).text() if self.editor_table.item(row, 7) else ""
        
        # Extract path columns (8-20)
        path_fields = [
            "p1_profile", "p2_profile", "desktop_ctrl", 
            "game_monitor_cfg", "desktop_monitor_cfg", 
            "post1", "post2", "post3", 
            "pre1", "pre2", "pre3", 
            "just_after", "just_before"
        ]
        
        # Extract each path column's raw text
        for i, field in enumerate(path_fields, 8):
            cell_item = self.editor_table.item(row, i)
            if cell_item:
                cell_text = cell_item.text()
                # Print debug info for each cell
                print(f"Row {row}, Column {i} ({field}): '{cell_text}'")
                game_data[field] = cell_text
            else:
                print(f"Row {row}, Column {i} ({field}): No cell item")
                game_data[field] = ""
        
        # Get run wait flags for pre/post launch apps
        for i in range(1, 4):
            game_data[f'pre{i}_run_wait'] = get_checkbox_value(row, 16 + i)  # Columns 17, 18, 19
            game_data[f'post{i}_run_wait'] = get_checkbox_value(row, 13 + i)  # Columns 14, 15, 16
        
        # Get run wait flags for just after/before apps
        game_data['just_after_run_wait'] = get_checkbox_value(row, 19)
        game_data['just_before_run_wait'] = get_checkbox_value(row, 20)
        
        # Get borderless status
        borderless_text = self.editor_table.item(row, 21).text() if self.editor_table.item(row, 21) else ""
        game_data['borderless'] = borderless_text
        
        # Get as_admin and no_tb
        game_data['as_admin'] = get_checkbox_value(row, 22)
        game_data['no_tb'] = get_checkbox_value(row, 23)
        
        # Debug output to verify data extraction
        print(f"Extracted game data for row {row}:")
        print(f"  Name: {game_data.get('name_override', '')}")
        print(f"  Executable: {game_data.get('executable', '')}")
        print(f"  Directory: {game_data.get('directory', '')}")
        
        # Debug output for path columns
        for field in path_fields:
            value = game_data.get(field, '')
            print(f"  {field}: '{value}'")
        
        return game_data

    def _save_config_on_radio_change(self, checked, key):
        """Save configuration when a radio button is toggled"""
        if checked:
            # Only save when a button is checked (not when unchecked)
            from Python.ui.config_manager import save_configuration

            save_configuration(self)


    def on_create_button_clicked(self):
        """Handle the Create button click"""
        # Get selected rows
        selected_rows = []
        for row in range(self.editor_table.rowCount()):
            include_widget = self.editor_table.cellWidget(row, 0)
            if include_widget:
                checkbox = include_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_rows.append(row)
        
        if not selected_rows:
            QMessageBox.warning(self, "No Games Selected", "Please select at least one game to process.")
            return
        
        # Get the selected games data
        selected_games = []
        for row in selected_rows:
            game_data = self._extract_game_data_from_row(row)
            selected_games.append(game_data)
        
        # Debug output to verify selected games
        print(f"Selected {len(selected_games)} games for processing")
        for i, game in enumerate(selected_games):
            print(f"Game {i+1}: {game.get('name_override', '')}")
            # Print path columns for debugging
            path_fields = [
                "p1_profile", "p2_profile", "desktop_ctrl", 
                "game_monitor_cfg", "desktop_monitor_cfg", 
                "post1", "post2", "post3", 
                "pre1", "pre2", "pre3", 
                "just_after", "just_before"
            ]
            for field in path_fields:
                print(f"  {field}: {game.get(field, '')}")
        
        # Call create_all with the selected games
        result = self.creation_controller.create_all(selected_games)
        
        # Show a summary message
        if result['failed_count'] > 0:
            QMessageBox.warning(self, "Creation Complete", f"{result['failed_count']} games failed to process.")
        else:
            QMessageBox.information(self, "Creation Complete", "All selected games processed successfully.")

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
            pass
        
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

            except Exception as e:
                pass
        
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

            except Exception as e:
                pass
        
        # Backup normalized index if it exists
        if os.path.exists(normalized_index_path):
            backup_path = normalized_index_path + ".old"
            try:
                # Remove old backup if it exists
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                
                # Create backup
                shutil.copy2(normalized_index_path, backup_path)

            except Exception as e:
                pass


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

                except Exception as e:
                    pass
            
            if os.path.exists(normalized_index_path):
                try:
                    os.remove(normalized_index_path)
                    files_deleted += 1

                except Exception as e:
                    pass
            
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

                    self.statusBar().showMessage("Steam JSON file deleted", 5000)
                except Exception as e:
                    self.statusBar().showMessage(f"Error deleting Steam JSON: {str(e)}", 5000)

            else:
                self.statusBar().showMessage("Steam JSON file not found", 5000)

    def _populate_editor_table_from_data(self, data):
        """Populate the editor table from the loaded data"""
        # Clear the table
        self.editor_table.setRowCount(0)
        
        # Add rows to the table
        for row_index, row_data in enumerate(data):
            self.editor_table.insertRow(row_index)
            
            # Set the include checkbox
            include_checkbox = QCheckBox()
            include_checkbox.setChecked(row_data.get("include", False))
            include_checkbox_widget = QWidget()
            include_checkbox_layout = QHBoxLayout(include_checkbox_widget)
            include_checkbox_layout.addWidget(include_checkbox)
            include_checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            include_checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.editor_table.setCellWidget(row_index, 0, include_checkbox_widget)
            
            # Set the text fields
            self.editor_table.setItem(row_index, 1, QTableWidgetItem(str(row_data.get("executable", ""))))
            self.editor_table.setItem(row_index, 2, QTableWidgetItem(str(row_data.get("directory", ""))))
            self.editor_table.setItem(row_index, 3, QTableWidgetItem(str(row_data.get("steam_title", ""))))
            self.editor_table.setItem(row_index, 4, QTableWidgetItem(str(row_data.get("name_override", ""))))
            self.editor_table.setItem(row_index, 5, QTableWidgetItem(str(row_data.get("options", ""))))
            self.editor_table.setItem(row_index, 6, QTableWidgetItem(str(row_data.get("arguments", ""))))
            self.editor_table.setItem(row_index, 7, QTableWidgetItem(str(row_data.get("steam_id", ""))))
            
            # Set path fields with their indicators
            path_indicators = row_data.get("path_indicators", {})
            path_fields = [
                "p1_profile", "p2_profile", "desktop_ctrl", 
                "game_monitor_cfg", "desktop_monitor_cfg", 
                "post1", "post2", "post3", 
                "pre1", "pre2", "pre3", 
                "just_after", "just_before"
            ]
            
            for i, field in enumerate(path_fields, 8):
                indicator = path_indicators.get(f"col_{i}_indicator", "<")
                value = str(row_data.get(field, ""))
                
                # Set the item with the indicator + value
                self.editor_table.setItem(row_index, i, QTableWidgetItem(indicator + value))
            
            # Set the borderless field
            borderless_value = row_data.get("borderless", "")
            self.editor_table.setItem(row_index, 21, QTableWidgetItem(str(borderless_value)))
            
            # Set the as_admin checkbox
            as_admin_checkbox = QCheckBox()
            as_admin_checkbox.setChecked(row_data.get("as_admin", False))
            as_admin_checkbox_widget = QWidget()
            as_admin_checkbox_layout = QHBoxLayout(as_admin_checkbox_widget)
            as_admin_checkbox_layout.addWidget(as_admin_checkbox)
            as_admin_checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            as_admin_checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.editor_table.setCellWidget(row_index, 22, as_admin_checkbox_widget)
            
            # Set the no_tb checkbox
            no_tb_checkbox = QCheckBox()
            no_tb_checkbox.setChecked(row_data.get("no_tb", False))
            no_tb_checkbox_widget = QWidget()
            no_tb_checkbox_layout = QHBoxLayout(no_tb_checkbox_widget)
            no_tb_checkbox_layout.addWidget(no_tb_checkbox)
            no_tb_checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_tb_checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.editor_table.setCellWidget(row_index, 23, no_tb_checkbox_widget)
