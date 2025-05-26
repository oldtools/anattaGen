"# This is a new version of main_window.py" 

import sys
import os
import re
import traceback
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QFileDialog, 
    QMenu, QTableWidgetItem, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QCoreApplication

# NLTK for Porter Stemmer
from nltk.stem.porter import PorterStemmer

# Import the UI modules
from Python.ui.setup_tab_ui import populate_setup_tab
from Python.ui.deployment_tab_ui import populate_deployment_tab
from Python.ui.editor_tab_ui import populate_editor_tab
from Python.ui.config_manager import load_initial_config, show_import_configuration_dialog, show_save_configuration_dialog
from Python.ui.index_manager import save_index, backup_index, delete_all_indexes, load_index
from Python.ui.name_utils import normalize_name_for_matching
from Python.ui.game_indexer import (
    index_sources_with_ui_updates, get_editor_table_data, load_set_file, 
    add_executable_to_editor_table, create_status_widget
)
from Python.ui.steam_cache import SteamCacheManager, STEAM_FILTERED_TXT, NORMALIZED_INDEX_CACHE
from Python.ui.steam_processor import SteamProcessor
from Python.ui.steam_utils import locate_and_exclude_manager_config

class MainWindow(QMainWindow):
    # Column indices for the editor table
    COL_INCLUDE = 0         # Checkbox
    COL_EXEC_NAME = 1       # Executable Name
    COL_DIRECTORY = 2       # Directory (Executable Path)
    COL_STEAM_NAME = 3      # Steam Name
    COL_NAME_OVERRIDE = 4   # Name Override
    COL_OPTIONS = 5         # Options
    COL_ARGUMENTS = 6       # Arguments
    COL_STEAM_ID = 7        # Steam ID
    COL_P1_PROFILE = 8      # P1 Profile
    COL_P2_PROFILE = 9      # P2 Profile
    COL_DESKTOP_CTRL = 10   # Desktop CTRL
    COL_GAME_MON_CFG = 11   # Game Monitor CFG
    COL_DESK_MON_CFG = 12   # Desktop Monitor CFG
    COL_POST_1 = 13         # Post-Launch App 1
    COL_POST_2 = 14         # Post-Launch App 2
    COL_POST_3 = 15         # Post-Launch App 3
    COL_PRE_1 = 16          # Pre-Launch App 1
    COL_PRE_2 = 17          # Pre-Launch App 2
    COL_PRE_3 = 18          # Pre-Launch App 3
    COL_JUST_AFTER = 19     # Just After App
    COL_JUST_BEFORE = 20    # Just Before App
    # COL_AS_ADMIN = 21 (Implicitly handled by add_executable_to_editor_table)
    # COL_NO_TB = 22    (Implicitly handled by add_executable_to_editor_table)

    def __init__(self):
        super().__init__()
        
        # Initialize data structures
        self.steam_title_cache = {}
        self.normalized_steam_match_index = {}
        self.filtered_steam_cache_file_path = None # Initialize Steam cache file path
        self.steam_json_file_path = None # Initialize Steam JSON file path
        self.found_executables_cache = set()

        # Initialize Steam-related managers
        self.steam_cache_manager = SteamCacheManager(self)
        self.steam_processor = SteamProcessor(self, self.steam_cache_manager)
        
        # Initialize stemmer for text normalization
        self.stemmer = PorterStemmer()
        
        # Load set files early
        self._load_set_files()
        
        # Setup UI
        self._setup_ui()
        
        # Load initial configuration
        load_initial_config(self)
        
        # Populate the editor table from index if it exists
        self._populate_editor_table_from_index()

    def _setup_ui(self):
        self.setWindowTitle("Game Environment Manager")
        self.setGeometry(100, 100, 950, 750)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.setup_tab = QWidget()
        self.deployment_tab = QWidget()
        self.editor_tab = QWidget()

        self.tabs.addTab(self.setup_tab, "Setup")
        self.tabs.addTab(self.deployment_tab, "Deployment")
        self.tabs.addTab(self.editor_tab, "Editor")

        populate_setup_tab(self)
        populate_deployment_tab(self)
        populate_editor_tab(self)

        # Add Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")

    def _load_set_files(self):
        """Load all set files (exclude_exe.set, folder_exclude.set, demoted.set, release_groups.set)"""
        # load_set_file is imported at the top of the file.
        
        # Load exclusion lists
        self.exclude_exe_set = load_set_file('Python/exclude_exe.set')
        self.folder_exclude_set = load_set_file('Python/folder_exclude.set')
        self.demoted_set = load_set_file('Python/demoted.set')
        self.release_groups_set = load_set_file('Python/release_groups.set')
        
        # Log the counts
        print(f"Loaded set files: exclude_exe.set ({len(self.exclude_exe_set)}), "
              f"folder_exclude.set ({len(self.folder_exclude_set)}), "
              f"demoted.set ({len(self.demoted_set)}), "
              f"release_groups.set ({len(self.release_groups_set)})")

    def _add_new_app_dialog(self, target_line_edit, app_type_name):
        # QFileDialog needs a parent window
        path, _ = QFileDialog.getOpenFileName(self, f"Select Custom {app_type_name} Application")
        if path:
            target_line_edit.setText(path)
            print(f"Custom {app_type_name} selected: {path}")

    def _normalize_name_for_matching(self, name: str) -> str:
        # Use the utility function from name_utils.py
        return normalize_name_for_matching(name, self.stemmer)

    def _on_editor_table_cell_left_click(self, row, column):
        """Handle left-click events on editor table cells"""
        # File selection columns
        file_selection_columns = {
            self.COL_DIRECTORY: "Select Game Executable",
            self.COL_P1_PROFILE: "Select Player 1 Profile",
            self.COL_P2_PROFILE: "Select Player 2 Profile",
            self.COL_DESKTOP_CTRL: "Select Desktop Control Profile",
            self.COL_GAME_MON_CFG: "Select Game Monitor Config",
            self.COL_DESK_MON_CFG: "Select Desktop Monitor Config",
            self.COL_POST_1: "Select Post-Launch App 1",
            self.COL_POST_2: "Select Post-Launch App 2",
            self.COL_POST_3: "Select Post-Launch App 3",
            self.COL_PRE_1: "Select Pre-Launch App 1",
            self.COL_PRE_2: "Select Pre-Launch App 2",
            self.COL_PRE_3: "Select Pre-Launch App 3",
            self.COL_JUST_AFTER: "Select Just After App",
            self.COL_JUST_BEFORE: "Select Just Before App"
        }
        
        if column in file_selection_columns:
            # Get current value
            current_value = self.editor_table.item(row, column).text() if self.editor_table.item(row, column) else ""
            
            # Determine file filter based on column
            file_filter = "All Files (*)"
            if column == self.COL_DIRECTORY:
                file_filter = "Executables (*.exe);;All Files (*)"
            elif column in [self.COL_P1_PROFILE, self.COL_P2_PROFILE, self.COL_DESKTOP_CTRL]:  # Profile columns
                file_filter = "Profile Files (*.json *.xml *.cfg);;All Files (*)"
            elif column in [self.COL_GAME_MON_CFG, self.COL_DESK_MON_CFG]:  # Monitor config columns
                file_filter = "Config Files (*.cfg *.ini *.json);;All Files (*)"
            elif column in [self.COL_POST_1, self.COL_POST_2, self.COL_POST_3, 
                            self.COL_PRE_1, self.COL_PRE_2, self.COL_PRE_3, 
                            self.COL_JUST_AFTER, self.COL_JUST_BEFORE]:  # App columns
                file_filter = "Executables (*.exe *.bat *.cmd);;All Files (*)"
            
            # Show file dialog
            new_path, _ = QFileDialog.getOpenFileName(
                self, 
                file_selection_columns[column], 
                os.path.dirname(current_value) if current_value else "", 
                file_filter
            )
            
            if new_path:
                # Update the cell with the new path
                self.editor_table.setItem(row, column, QTableWidgetItem(new_path))
                
                # Special handling for Directory column
                if column == self.COL_DIRECTORY:
                    # Update executable name
                    exec_name = os.path.basename(new_path)
                    self.editor_table.setItem(row, self.COL_EXEC_NAME, QTableWidgetItem(exec_name))
                    
                    # Try to match with Steam
                    if hasattr(self, 'normalized_steam_match_index') and self.normalized_steam_match_index:
                        dir_name = os.path.basename(os.path.dirname(new_path))
                        norm_dir_name = normalize_name_for_matching(dir_name, self.stemmer)
                        
                        if norm_dir_name in self.normalized_steam_match_index:
                            steam_match = self.normalized_steam_match_index[norm_dir_name]["name"]
                            steam_id = self.normalized_steam_match_index[norm_dir_name]["id"]
                            
                            # Update Steam name and ID
                            self.editor_table.setItem(row, self.COL_STEAM_NAME, QTableWidgetItem(steam_match))
                            self.editor_table.setItem(row, self.COL_STEAM_ID, QTableWidgetItem(steam_id))
                            
                            # Clear name override if we have a Steam match
                            self.editor_table.setItem(row, self.COL_NAME_OVERRIDE, QTableWidgetItem(""))
            
                self.statusBar().showMessage(f"Updated {file_selection_columns[column]}: {new_path}", 3000)

    def _on_editor_table_custom_context_menu(self, position):
        """Handle right-click context menu in the editor table"""
        # Get the row and column that was clicked
        row = self.editor_table.rowAt(position.y())
        col = self.editor_table.columnAt(position.x())
        
        # Create context menu
        context_menu = QMenu(self)
        
        if row >= 0:
            item = self.editor_table.item(row, self.COL_EXEC_NAME)  # The name column
            if item and item.text():
                omit_action = context_menu.addAction(f"Omit \"{item.text()}\"")
                omit_action.triggered.connect(lambda: self._handle_omit_action(row, col, item.text()))
                
                context_menu.exec(self.editor_table.viewport().mapToGlobal(position))

    def _handle_omit_action(self, row, column, item_name):
        print(f"Omitting {item_name} from consideration")
        # Add to folder_exclude_set (not usable here)
        self.folder_exclude_set.add(item_name)
        
        # Remove the row from the table
        self.editor_table.removeRow(row)
        self.statusBar().showMessage(f"Omitted {item_name} from consideration", 3000)

    def _on_append_index(self):
        index_sources_with_ui_updates(self)
        data = get_editor_table_data(self)
        # Append to existing index file if it exists
        if os.path.exists('current.index'):
            print("Appending to existing index file")
            backup_index()
        
        save_index(self, data)

    def _on_clear_listview(self):
        # Clear the editor table
        self.editor_table.setRowCount(0)
        self.statusBar().showMessage("Cleared editor table", 3000)

    def _on_delete_indexes(self):
        delete_all_indexes(self)

    def _on_editor_table_edited(self, item):
        print(f"Editor table edited: {item.row()}, {item.column()}, {item.text()}")

    def _import_configuration_dialog(self):
        show_import_configuration_dialog(self)

    def _show_save_configuration_dialog(self):
        show_save_configuration_dialog(self)

    def _load_index(self):
        load_index(self)

    def _load_filtered_steam_cache(self):
        return self.steam_cache_manager.load_filtered_steam_cache()

    def _prompt_and_process_steam_json(self):
        self.steam_processor.prompt_and_process_steam_json()

    def _process_steam_json_file(self, input_json_path: str):
        self.steam_processor.process_steam_json_file(input_json_path)

    def _locate_and_exclude_manager_config(self):
        locate_and_exclude_manager_config(self)

    def _load_set_file(self, filename: str) -> set:
        return load_set_file(self, filename)

    def _index_sources(self):
        """Handle the Index Sources button click from the Deployment tab"""
        # Show immediate feedback
        self.statusBar().showMessage("Starting indexing process...", 3000)
        print("Index Sources button clicked")
        
        # Process any pending UI events before starting the intensive operation
        QCoreApplication.processEvents() # QCoreApplication moved to top imports
        
        # index_sources_with_ui_updates is imported at the top of the file.
        # The try-except block for its import has been removed.
        
        # Switch to the Editor tab first
        try:
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "Editor":
                    self.tabs.setCurrentIndex(i)
                    print("Switched to Editor tab")
                    break
            
            # Process events again to ensure tab switch is visible
            QCoreApplication.processEvents()
        except Exception as e:
            print(f"Error switching tabs: {e}")
        
        # Use the enhanced indexing function with UI updates
        try:
            print("Starting indexing with UI updates")
            # This function handles its own progress dialog and UI updates
            result = index_sources_with_ui_updates(self)
            print(f"Indexing completed with result: {result}")
        except Exception as e:
            # QMessageBox and traceback are imported at the top of the file.
            print(f"Exception during indexing: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Indexing Error", f"An error occurred during indexing:\n{str(e)}")
            self.statusBar().showMessage(f"Indexing failed: {str(e)}", 5000)

    def _get_editor_table_data(self):
        return get_editor_table_data(self.editor_table)

    def _save_editor_table_to_index(self):
        save_index(self, self._get_editor_table_data())

    def _update_steam_json_cache(self):
        self.steam_cache_manager.load_filtered_steam_cache()

    def closeEvent(self, event):
        self._save_editor_table_to_index()
        event.accept()

    def _populate_editor_table_from_index(self):
        # If current.index exists, load it
        if os.path.exists('current.index'):
            try:
                with open('current.index', 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split('|')
                            if len(parts) >= 8:
                                # Convert string to boolean for checkbox values
                                include_checked = parts[0].lower() == "true"
                                exec_name = parts[1]
                                directory = parts[2]
                                steam_name = parts[3]
                                name_override = parts[4]
                                options = parts[5]
                                arguments = parts[6]
                                steam_id = parts[7]
                                as_admin = parts[8].lower() == "true" if len(parts) > 8 else False
                                no_tb = parts[9].lower() == "true" if len(parts) > 9 else False
                                
                                add_executable_to_editor_table(
                                    self, include_checked, exec_name, directory, steam_name, 
                                    name_override, options, arguments, steam_id, as_admin, no_tb
                                )
                
                self.statusBar().showMessage("Loaded index file", 3000)
            except Exception as e:
                self.statusBar().showMessage(f"Error loading index: {e}", 5000)
                print(f"Error loading index: {e}")

    def _add_executable_to_editor_table(self, include_checked, exec_name, directory, steam_name, name_override, options, arguments, steam_id, as_admin=False, no_tb=False):
        """Add an executable to the editor table (delegates to game_indexer.py)"""
        # add_executable_to_editor_table is imported at the top of the file.
        add_executable_to_editor_table(
            self, include_checked, exec_name, directory, steam_name, 
            name_override, options, arguments, steam_id, as_admin, no_tb
        )

    def _on_index_sources(self):
        """Handle the Index Sources button click"""
        # index_sources_with_ui_updates is imported at the top of the file.
        index_sources_with_ui_updates(self)

    def _on_editor_table_header_click(self, section):
        """Handle clicks on table headers for multi-item selection"""
        # File selection columns
        file_selection_columns = {
            8: "Select Player 1 Profile for All",  # P1 Profile
            9: "Select Player 2 Profile for All",  # P2 Profile
            10: "Select Desktop Control Profile for All",  # Desktop CTRL
            11: "Select Game Monitor Config for All",  # Game Monitor CFG
            12: "Select Desktop Monitor Config for All",  # Desktop Monitor CFG
            13: "Select Post-Launch App 1 for All",  # Post 1
            14: "Select Post-Launch App 2 for All",  # Post 2
            15: "Select Post-Launch App 3 for All",  # Post 3
            16: "Select Pre-Launch App 1 for All",  # Pre 1
            17: "Select Pre-Launch App 2 for All",  # Pre 2
            18: "Select Pre-Launch App 3 for All",  # Pre 3
            19: "Select Just After App for All",  # Just After
            20: "Select Just Before App for All"  # Just Before
        }
        
        if section in file_selection_columns:
            # Determine file filter based on column
            file_filter = "All Files (*)"
            if section in [8, 9, 10]:  # Profile columns
                file_filter = "Profile Files (*.json *.xml *.cfg);;All Files (*)"
            elif section in [11, 12]:  # Monitor config columns
                file_filter = "Config Files (*.cfg *.ini *.json);;All Files (*)"
            elif section in [13, 14, 15, 16, 17, 18, 19, 20]:  # App columns
                file_filter = "Executables (*.exe *.bat *.cmd);;All Files (*)"
            
            # Show file dialog
            new_path, _ = QFileDialog.getOpenFileName(
                self, 
                file_selection_columns[section], 
                "", 
                file_filter
            )
            
            if new_path:
                # Update all rows with the new path
                for row in range(self.editor_table.rowCount()):
                    self.editor_table.setItem(row, section, QTableWidgetItem(new_path))
                
                # Special handling for Directory column
                if section == 2:
                    # Update executable name for all rows
                    for row in range(self.editor_table.rowCount()):
                        exec_name = os.path.basename(new_path)
                        self.editor_table.setItem(row, 1, QTableWidgetItem(exec_name))
                    
                    # Try to match with Steam for all rows
                    if hasattr(self, 'normalized_steam_match_index') and self.normalized_steam_match_index:
                        dir_name = os.path.basename(os.path.dirname(new_path))
                        norm_dir_name = normalize_name_for_matching(dir_name, self.stemmer)
                        
                        if norm_dir_name in self.normalized_steam_match_index:
                            steam_match = self.normalized_steam_match_index[norm_dir_name]["name"]
                            steam_id = self.normalized_steam_match_index[norm_dir_name]["id"]
                            
                            # Update Steam name and ID for all rows
                            for row in range(self.editor_table.rowCount()):
                                self.editor_table.setItem(row, 3, QTableWidgetItem(steam_match))
                                self.editor_table.setItem(row, 7, QTableWidgetItem(steam_id))
                            
                            # Clear name override if we have a Steam match
                            for row in range(self.editor_table.rowCount()):
                                self.editor_table.setItem(row, 4, QTableWidgetItem(""))

    def _regenerate_name(self, row):
        """Regenerate the name override based on executable path or Steam name"""
        from Python.ui.name_processor import NameProcessor
        
        # Get executable path and Steam name
        exec_path_item = self.editor_table.item(row, self.COL_DIRECTORY)
        exec_path = exec_path_item.text() if exec_path_item else ""
        steam_name_item = self.editor_table.item(row, self.COL_STEAM_NAME)
        steam_name = steam_name_item.text() if steam_name_item else ""
        
        # Create a name processor
        name_processor = NameProcessor(
            release_groups_set=self.release_groups_set,
            folder_exclude_set=self.folder_exclude_set
        )
        
        # Generate name override
        if steam_name:
            # If we have a Steam name, use it directly but make it safe for Windows filenames
            name_override = name_processor.get_display_name(steam_name)
            print(f"Regenerated name override from Steam name: '{steam_name}' -> '{name_override}'")
        else:
            # Otherwise, derive from path with more aggressive cleaning
            dir_path = os.path.dirname(exec_path) if os.path.isfile(exec_path) else exec_path
            dir_name = os.path.basename(dir_path)
            name_override = name_processor.get_display_name(dir_name)
            print(f"Regenerated name override from path: '{dir_path}' -> '{name_override}'")
        
        # Update the name override
        self.editor_table.setItem(row, self.COL_NAME_OVERRIDE, QTableWidgetItem(name_override))
        self.statusBar().showMessage(f"Regenerated name: {name_override}", 3000)

    def _regenerate_all_names(self):
        """Regenerate all name overrides in the editor table"""
        row_count = self.editor_table.rowCount()
        if row_count == 0:
            self.statusBar().showMessage("No entries to process", 3000)
            return
        
        for row in range(row_count):
            self._regenerate_name(row)
        
        self.statusBar().showMessage(f"Regenerated {row_count} names", 3000)

    def _debug_set_files(self):
        """Debug method to print the contents of set files"""
        print("\nDEBUG: Set file contents")
        print("exclude_exe.set items:")
        for item in sorted(self.exclude_exe_set):
            print(f"  - '{item}'")
        
        print("\nfolder_exclude.set items:")
        for item in sorted(self.folder_exclude_set):
            print(f"  - '{item}'")
        
        print("\ndemoted.set items:")
        for item in sorted(self.demoted_set):
            print(f"  - '{item}'")
        
        print("\nrelease_groups.set items:")
        for item in sorted(self.release_groups_set):
            print(f"  - '{item}'")
        
        self.statusBar().showMessage("Set file contents printed to console", 3000)

    def _debug_steam_matching(self):
        """Debug method to test Steam matching for a sample directory"""
        print("\nDEBUG: Steam Matching Test")
        
        if not hasattr(self, 'normalized_steam_match_index') or not self.normalized_steam_match_index:
            print("No normalized Steam match index available. Please load Steam data first.")
            self.statusBar().showMessage("No Steam data loaded", 3000)
            return
        
        # Get all directories from the editor table
        directories = []
        for row in range(self.editor_table.rowCount()):
            dir_path_item = self.editor_table.item(row, self.COL_DIRECTORY)
            if dir_path_item:
                dir_path = dir_path_item.text()
                if dir_path and os.path.exists(dir_path):
                    dir_name = os.path.basename(os.path.dirname(dir_path))
                    directories.append((row, dir_path, dir_name))
        
        if not directories:
            print("No directories found in editor table")
            self.statusBar().showMessage("No directories to test", 3000)
            return
        
        # Test matching for each directory
        match_count = 0
        for row, dir_path, dir_name in directories:
            from Python.ui.name_utils import normalize_name_for_matching
            norm_dir_name = normalize_name_for_matching(dir_name, self.stemmer)
            
            print(f"\nTesting directory: '{dir_name}'")
            print(f"Normalized name: '{norm_dir_name}'")
            
            if norm_dir_name in self.normalized_steam_match_index:
                match_data = self.normalized_steam_match_index[norm_dir_name]
                print(f"MATCH FOUND: {match_data['name']} (ID: {match_data['id']})")
                match_count += 1
                
                # Update the editor table with the match
                self.editor_table.setItem(row, self.COL_STEAM_NAME, QTableWidgetItem(match_data['name']))
                self.editor_table.setItem(row, self.COL_STEAM_ID, QTableWidgetItem(match_data['id']))
                
                # Update name override if it's empty
                name_override_item = self.editor_table.item(row, self.COL_NAME_OVERRIDE)
                if not name_override_item or not name_override_item.text():
                    from Python.ui.name_utils import make_safe_filename
                    name_override = make_safe_filename(match_data['name'])
                    self.editor_table.setItem(row, self.COL_NAME_OVERRIDE, QTableWidgetItem(name_override))
            else:
                print("No match found")
                
                # Try to find partial matches
                partial_matches = []
                for key in self.normalized_steam_match_index.keys():
                    if norm_dir_name in key or key in norm_dir_name:
                        partial_matches.append((key, self.normalized_steam_match_index[key]))
                        if len(partial_matches) >= 3:  # Limit to 3 partial matches
                            break
                
                if partial_matches:
                    print("Potential partial matches:")
                    for i, (key, data) in enumerate(partial_matches):
                        print(f"  {i+1}. '{key}' -> {data['name']} (ID: {data['id']})")
                
                # If no Steam match, ensure name override is populated
                name_override_item = self.editor_table.item(row, self.COL_NAME_OVERRIDE)
                if not name_override_item or not name_override_item.text():
                    from Python.ui.name_processor import NameProcessor
                    
                    # Create name processor
                    name_processor = NameProcessor(
                        release_groups_set=self.release_groups_set,
                        folder_exclude_set=self.folder_exclude_set
                    )
                    
                    # Get directory name
                    # dir_path was already defined for the current row
                    # dir_name was already defined for the current row
                    
                    # Process the name
                    name_override = name_processor.get_display_name(dir_name) # Use existing dir_name
                    self.editor_table.setItem(row, self.COL_NAME_OVERRIDE, QTableWidgetItem(name_override))
        
        print(f"\nMatching complete: {match_count} matches found out of {len(directories)} directories")
        self.statusBar().showMessage(f"Steam matching test: {match_count}/{len(directories)} matches", 5000)
