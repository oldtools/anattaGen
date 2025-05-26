import os
import json
import time
import re
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QProgressDialog, QTableWidgetItem, QCheckBox, QComboBox, QPushButton, QLabel
from Python.ui.name_processor import NameProcessor
from Python.ui.steam_utils import locate_and_exclude_manager_config

def index_sources_with_ui_updates(main_window):
    """Index sources with UI updates and progress dialog"""
    # Reset cancellation flag
    main_window.indexing_cancelled = False
    main_window.indexing_in_progress = True
    
    # Disable editor table during indexing
    main_window.editor_table.setEnabled(False)
    
    # Create cancel button in status bar
    main_window.cancel_indexing_button = QPushButton("Cancel Indexing")
    main_window.cancel_indexing_button.clicked.connect(lambda: _confirm_cancel_indexing(main_window))
    main_window.statusBar().addPermanentWidget(main_window.cancel_indexing_button)
    main_window.cancel_indexing_button.show()
    
    # Create progress dialog
    main_window.indexing_progress = QProgressDialog("Preparing to index sources...", "Cancel", 0, 100, main_window)
    main_window.indexing_progress.setWindowTitle("Indexing Sources")
    main_window.indexing_progress.setWindowModality(Qt.WindowModality.WindowModal)
    main_window.indexing_progress.setMinimumDuration(0)
    main_window.indexing_progress.canceled.connect(lambda: setattr(main_window, 'indexing_cancelled', True))
    main_window.indexing_progress.setValue(0)
    main_window.indexing_progress.show()
    
    # Perform indexing
    result = _perform_indexing_with_updates(main_window)
    
    # Clean up
    if hasattr(main_window, 'indexing_progress'):
        main_window.indexing_progress.close()
        main_window.indexing_progress = None
    
    _finish_indexing(main_window)
    
    return result

def _perform_indexing_with_updates(main_window):
    """
    Perform the actual indexing with UI updates.
    
    Args:
        main_window: The main application window
    
    Returns:
        True if indexing completed successfully, False otherwise
    """
    # Reset cancellation flag
    main_window.indexing_cancelled = False
    
    # Check for filtered Steam cache or load Steam data
    if not hasattr(main_window, 'normalized_steam_match_index') or not main_window.normalized_steam_match_index:
        print("No normalized Steam match index found, attempting to load...")
        # Use the SteamCacheManager instance on main_window
        if not main_window.steam_cache_manager.load_filtered_steam_cache():
            main_window.statusBar().showMessage("No cached Steam data. Please load Steam JSON first.")
            return False
    
    # If requested, exclude games from selected manager
    selected_manager = main_window.other_managers_combo.currentText()
    if selected_manager != "(None)" and main_window.exclude_manager_checkbox.isChecked():
        main_window._locate_and_exclude_manager_config()
    
    # Clear the existing table
    main_window.editor_table.setRowCount(0)
    main_window.found_executables_cache = set()  # Reset cache
    
    # Process each source directory
    source_count = 0
    for i in range(main_window.source_dirs_combo.count()):
        if main_window.indexing_cancelled:
            break
        
        source_dir = main_window.source_dirs_combo.itemText(i)
        if os.path.exists(source_dir):
            source_count += traverse_source_directory(main_window, source_dir, source_dir)
    
    if main_window.indexing_cancelled:
        main_window.statusBar().showMessage("Indexing cancelled")
        return False
    
    if source_count > 0:
        main_window.statusBar().showMessage(f"Indexed {source_count} sources")
        return True
    else:
        main_window.statusBar().showMessage("No sources found or indexed")
        return False

def _confirm_cancel_indexing(main_window):
    """Show confirmation dialog for cancelling indexing"""
    from PyQt6.QtWidgets import QMessageBox
    reply = QMessageBox.question(
        main_window, 
        'Cancel Indexing',
        'Are you sure you want to cancel the indexing process?',
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        main_window.indexing_cancelled = True
        main_window.statusBar().showMessage("Indexing cancelled by user")

def _finish_indexing(main_window):
    """Clean up after indexing is complete or cancelled"""
    main_window.indexing_in_progress = False
    main_window.editor_table.setEnabled(True)
    
    # Hide cancel button
    if hasattr(main_window, 'cancel_indexing_button'):
        main_window.cancel_indexing_button.hide()
        # If it was added to status bar, remove it
        main_window.statusBar().removeWidget(main_window.cancel_indexing_button)

def traverse_source_directory(main_window, current_dir_path, source_root_path):
    """Traverse a source directory looking for executables"""
    # Initialize counter for executables added
    added_exe_count = 0
    
    # Check if indexing was cancelled
    if hasattr(main_window, 'indexing_cancelled') and main_window.indexing_cancelled:
        return 0
    
    # Process UI events periodically
    QCoreApplication.processEvents()
    
    # Create a name processor
    name_processor = NameProcessor(
        release_groups_set=main_window.release_groups_set,
        folder_exclude_set=main_window.folder_exclude_set,
        exclude_exe_set=main_window.exclude_exe_set
    )
    
    # Process the directory
    try:
        # Update progress dialog message if available
        if hasattr(main_window, 'indexing_progress') and main_window.indexing_progress:
            main_window.indexing_progress.setLabelText(f"Scanning: {current_dir_path}")
            QCoreApplication.processEvents()
        
        # Scan directory for executables
        with os.scandir(current_dir_path) as entries:
            for entry in entries:
                # Check if indexing was cancelled
                if hasattr(main_window, 'indexing_cancelled') and main_window.indexing_cancelled:
                    return added_exe_count
                
                try:
                    entry_path = os.path.join(current_dir_path, entry.name)
                    
                    # Skip excluded folders
                    if entry.is_dir(follow_symlinks=False):
                        # Check if folder should be excluded - exact match only
                        should_exclude = False
                        if hasattr(main_window, 'folder_exclude_set') and main_window.folder_exclude_set:
                            if entry.name.lower() in (item.lower() for item in main_window.folder_exclude_set if item):
                                print(f"Skipping excluded folder (exact match): {entry.name}")
                                should_exclude = True
                        
                        if not should_exclude:
                            # Recursively process subdirectory
                            added_exe_count += traverse_source_directory(main_window, entry_path, source_root_path)
                    
                    elif entry.is_file(follow_symlinks=False) and entry.name.lower().endswith('.exe'):
                        # Process executable file
                        exec_name = entry.name
                        exec_full_path = os.path.normpath(entry_path)
                        exec_full_path_lower = exec_full_path.lower()
                        
                        # Debug output for filtering
                        print(f"Found executable: {exec_name}")

                        # Skip if already processed
                        if hasattr(main_window, 'found_executables_cache') and exec_full_path_lower in main_window.found_executables_cache:
                            print(f"Skipping already processed: {exec_name}")
                            continue
                        
                        # Skip if in exclude_exe_set
                        should_skip = False
                        if hasattr(main_window, 'exclude_exe_set') and main_window.exclude_exe_set:
                            for not_item in main_window.exclude_exe_set:
                                if not_item and not_item.lower() in exec_name.lower():
                                    print(f"Skipping due to exclude_exe.set match: {exec_name} contains '{not_item}'")
                                    should_skip = True
                                    break
                        if should_skip:
                            continue
                        
                        # Get directory path
                        dir_path = os.path.dirname(exec_full_path)
                        
                        # Update progress dialog message
                        if hasattr(main_window, 'indexing_progress') and main_window.indexing_progress:
                            main_window.indexing_progress.setLabelText(f"Processing: {exec_name}")
                            QCoreApplication.processEvents()
                        
                        # Determine if this should be checked by default (not in demoted_set)
                        include_checked = True
                        if hasattr(main_window, 'demoted_set') and main_window.demoted_set:
                            for nor_item in main_window.demoted_set:
                                # Skip very short items (less than 3 characters)
                                if not nor_item or len(nor_item) < 3:
                                    continue
                                    
                                # Check if the directory name contains the demoted item
                                dir_name = os.path.basename(dir_path)
                                if nor_item.lower() in dir_name.lower():
                                    include_checked = False
                                    print(f"Demoting due to demoted.set match: '{dir_name}' contains '{nor_item}'")
                                    break
                        
                        # Get directory name for display name processing
                        dir_name = os.path.basename(dir_path)

                        # Process the name to get a clean display name
                        name_override = name_processor.get_display_name(dir_name)
                        print(f"Name processor result: '{dir_name}' -> '{name_override}'")

                        # Try to match with Steam
                        steam_name = ""
                        steam_id = ""

                        if hasattr(main_window, 'normalized_steam_match_index') and main_window.normalized_steam_match_index:
                            # Get the match name using the name processor - use the cleaned name_override
                            match_name = name_processor.get_match_name(name_override)
                            print(f"Match name transformation: '{name_override}' -> '{match_name}'")
                            
                            # Check if we have a match in the normalized index
                            if match_name and match_name in main_window.normalized_steam_match_index:
                                match_data = main_window.normalized_steam_match_index[match_name]
                                steam_name = match_data["name"]
                                steam_id = match_data["id"]
                                print(f"STEAM MATCH FOUND: '{steam_name}' (ID: {steam_id})")
                                
                                # If we have a Steam match, use it for the name override
                                if steam_name:
                                    from Python.ui.name_utils import make_safe_filename
                                    name_override = make_safe_filename(steam_name)
                                    print(f"Using Steam name for override: '{steam_name}' -> '{name_override}'")
                            else:
                                # If no match with the processed name, try with the original directory name
                                # This is a fallback for cases where our processing might be too aggressive
                                from Python.ui.name_utils import normalize_name_for_matching
                                
                                # Use the already cleaned name_override instead of the original dir_name
                                # But DON'T use the stemmer for this fallback attempt to avoid over-processing
                                norm_dir_name = normalize_name_for_matching(name_override, None)  # Pass None instead of stemmer
                                
                                print(f"Looking for Steam match with cleaned name (no stemming): '{name_override}' -> normalized: '{norm_dir_name}'")
                                
                                if norm_dir_name and norm_dir_name in main_window.normalized_steam_match_index:
                                    match_data = main_window.normalized_steam_match_index[norm_dir_name]
                                    steam_name = match_data["name"]
                                    steam_id = match_data["id"]
                                    print(f"STEAM MATCH FOUND (fallback): '{steam_name}' (ID: {steam_id})")
                                    
                                    # If we have a Steam match, use it for the name override
                                    if steam_name:
                                        from Python.ui.name_utils import make_safe_filename
                                        name_override = make_safe_filename(steam_name)
                                        print(f"Using Steam name for override: '{steam_name}' -> '{name_override}'")

                        # Add to the editor table
                        add_executable_to_editor_table(
                            main_window,
                            include_checked=include_checked,
                            exec_name=exec_name,
                            directory=dir_path,
                            steam_name=steam_name,
                            name_override=name_override,
                            options="",
                            arguments="",
                            steam_id=steam_id,
                            as_admin=False,
                            no_tb=False
                        )
                        
                        # Add to cache
                        if hasattr(main_window, 'found_executables_cache'):
                            main_window.found_executables_cache.add(exec_full_path_lower)
                        
                        # Update counter
                        added_exe_count += 1
                        
                        # Process UI events after each executable
                        QCoreApplication.processEvents()
                        
                except PermissionError:
                    continue
                except Exception as e:
                    print(f"Error processing {entry_path}: {e}")
                    continue
    
    except PermissionError:
        print(f"Permission denied: {current_dir_path}")
    except Exception as e:
        print(f"Error traversing {current_dir_path}: {e}")
    
    return added_exe_count

def get_editor_table_data(editor_table):
    """Extract data from the editor table into a list of dictionaries"""
    data = []
    for row in range(editor_table.rowCount()):
        # Get borderless value from combo box
        borderless_widget = editor_table.cellWidget(row, 21)
        borderless_value = borderless_widget.currentText() if isinstance(borderless_widget, QComboBox) else "No"
        
        row_data = {
            "include": editor_table.cellWidget(row, 0).isChecked() if editor_table.cellWidget(row, 0) else False,
            "executable": editor_table.item(row, 1).text() if editor_table.item(row, 1) else "",
            "directory": editor_table.item(row, 2).text() if editor_table.item(row, 2) else "",
            "steam_title": editor_table.item(row, 3).text() if editor_table.item(row, 3) else "",
            "name_override": editor_table.item(row, 4).text() if editor_table.item(row, 4) else "",
            "options": editor_table.item(row, 5).text() if editor_table.item(row, 5) else "",
            "arguments": editor_table.item(row, 6).text() if editor_table.item(row, 6) else "",
            "steam_id": editor_table.item(row, 7).text() if editor_table.item(row, 7) else "",
            "p1_profile": editor_table.item(row, 8).text() if editor_table.item(row, 8) else "",
            "p2_profile": editor_table.item(row, 9).text() if editor_table.item(row, 9) else "",
            "desktop_ctrl": editor_table.item(row, 10).text() if editor_table.item(row, 10) else "",
            "game_monitor_cfg": editor_table.item(row, 11).text() if editor_table.item(row, 11) else "",
            "desktop_monitor_cfg": editor_table.item(row, 12).text() if editor_table.item(row, 12) else "",
            "post1": editor_table.item(row, 13).text() if editor_table.item(row, 13) else "",
            "post2": editor_table.item(row, 14).text() if editor_table.item(row, 14) else "",
            "post3": editor_table.item(row, 15).text() if editor_table.item(row, 15) else "",
            "pre1": editor_table.item(row, 16).text() if editor_table.item(row, 16) else "",
            "pre2": editor_table.item(row, 17).text() if editor_table.item(row, 17) else "",
            "pre3": editor_table.item(row, 18).text() if editor_table.item(row, 18) else "",
            "just_after": editor_table.item(row, 19).text() if editor_table.item(row, 19) else "",
            "just_before": editor_table.item(row, 20).text() if editor_table.item(row, 20) else "",
            "borderless": borderless_value,
            "as_admin": editor_table.cellWidget(row, 22).isChecked() if editor_table.cellWidget(row, 22) else False,
            "no_tb": editor_table.cellWidget(row, 23).isChecked() if editor_table.cellWidget(row, 23) else False
        }
        data.append(row_data)
    return data

def load_set_file(filename):
    """Load a .set file into a set of strings"""
    result = set()
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        result.add(line)
        else:
            # Try looking in the project root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            alt_path = os.path.join(project_root, filename)
            
            if os.path.exists(alt_path):
                with open(alt_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            result.add(line)
                print(f"Loaded {len(result)} items from {alt_path}")
            else:
                print(f"Warning: {filename} not found at {filename} or {alt_path}")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    
    print(f"Loaded {len(result)} items from {filename}")
    return result

def add_executable_to_editor_table(main_window, include_checked=True, exec_name="", directory="", 
                                  steam_name="", name_override="", options="", arguments="", 
                                  steam_id="", as_admin=False, no_tb=False, update_ui=True):
    """
    Add an executable to the editor table
    
    Args:
        main_window: The main application window
        include_checked: Whether the include checkbox should be checked
        exec_name: The executable name
        directory: The directory path
        steam_name: The Steam name
        name_override: The name override
        options: Additional options
        arguments: Command line arguments
        steam_id: The Steam ID
        as_admin: Whether to run as admin
        no_tb: Whether to disable taskbar integration
        update_ui: Whether to update the UI after adding
        
    Returns:
        The row index of the added item
    """
    # Debug output to trace the function call
    print(f"DEBUG: add_executable_to_editor_table called with exec_name={exec_name}")
    
    # Get the current row count
    row = main_window.editor_table.rowCount()
    main_window.editor_table.insertRow(row)
    
    # Create include checkbox
    include_checkbox = QCheckBox()
    include_checkbox.setChecked(include_checked)
    include_checkbox.setStyleSheet("margin-left:10px; margin-right:10px;")
    main_window.editor_table.setCellWidget(row, 0, include_checkbox)
    
    # Set the executable name
    main_window.editor_table.setItem(row, 1, QTableWidgetItem(exec_name))
    
    # Set the directory
    main_window.editor_table.setItem(row, 2, QTableWidgetItem(directory))
    
    # Set the Steam name
    main_window.editor_table.setItem(row, 3, QTableWidgetItem(steam_name))
    
    # Set the name override
    main_window.editor_table.setItem(row, 4, QTableWidgetItem(name_override))
    
    # Set the Steam ID
    main_window.editor_table.setItem(row, main_window.COL_STEAM_ID, QTableWidgetItem(steam_id))
    
    # Process UI events to ensure table updates
    QCoreApplication.processEvents()
    
    # Update UI if requested
    if update_ui:
        main_window.editor_table.scrollToItem(main_window.editor_table.item(row, 0))
        main_window.editor_table.selectRow(row)
    
    print(f"DEBUG: Row {row} added to table with exec_name={exec_name}")
    
    return row

def create_status_widget(text="", status_type="normal"):
    """Create a status widget with appropriate styling"""
    from PyQt6.QtWidgets import QLabel
    
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    if status_type == "error":
        label.setStyleSheet("background-color: #ffcccc; color: #990000;")
    elif status_type == "warning":
        label.setStyleSheet("background-color: #ffffcc; color: #999900;")
    elif status_type == "success":
        label.setStyleSheet("background-color: #ccffcc; color: #009900;")
    else:
        label.setStyleSheet("background-color: #f0f0f0; color: #000000;")
    
    return label
