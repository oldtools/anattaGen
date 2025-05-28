from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QStatusBar, 
    QMessageBox, QMenu, QFileDialog, QTableWidgetItem, QCheckBox,
    QProgressDialog
)
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QCursor
import os

# Import tab population functions
from Python.ui.setup_tab_ui import populate_setup_tab
from Python.ui.deployment_tab_ui import populate_deployment_tab
from Python.ui.editor_tab_ui import populate_editor_tab
from Python.ui.config_manager import load_initial_config

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
        populate_deployment_tab(self, self.tabs)  # Pass self.tabs as the tab_widget argument
        populate_editor_tab(self)

        # Add Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")
        
    def _add_new_app_dialog(self, line_edit):
        """Handle the 'Add New...' option in app selection dropdowns"""
        # This is a placeholder for the actual implementation
        # It will be called when the user selects 'Add New...' in a dropdown
        pass
        
    def _prompt_and_process_steam_json(self):
        """Prompt the user to select a Steam JSON file and process it"""
        from Python.ui.steam_processor import SteamProcessor
        
        # Create processor if needed
        if not hasattr(self, 'steam_processor'):
            self.steam_processor = SteamProcessor(self, self.steam_cache_manager)
        
        # Process Steam JSON
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
            
            # Get as_admin and no_tb from columns 8-9 (if they exist)
            row_data["as_admin"] = False  # Default value
            row_data["no_tb"] = False     # Default value
            
            data.append(row_data)
        
        return data
        
    def _index_sources(self):
        """Index sources for games"""
        from Python.ui.game_indexer import index_sources
        index_sources(self)
        
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
            
            # Set as_admin and no_tb if they exist
            # These would typically be checkboxes or other widgets
        
        self.statusBar().showMessage(f"Loaded {len(data)} entries", 3000)
        
    def _save_editor_table_to_index(self):
        """Save the editor table data to the index file"""
        from Python.ui.index_manager import save_index
        
        # Get the data from the editor table
        data = self._get_editor_table_data()
        
        # Save the data to the index file
        save_index(self)
        
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
