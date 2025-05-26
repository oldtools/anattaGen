import os
import shutil
from datetime import datetime

INDEX_FILENAME = "current.index"
BACKUP_DIR = "index_backups"
PIPE_CHAR = "|"
SAFE_PIPE_CHAR = ""  # U+2502


def save_index(main_window_or_data, directory="."):
    """
    Save the table data to current.index, replacing all | with │.
    
    Args:
        main_window_or_data: Either MainWindow object or list of dicts/rows with game data
        directory: Directory to save the index file in (default: current dir)
    """
    # If we got the main_window, get the data from it
    data = main_window_or_data
    if hasattr(main_window_or_data, '_get_editor_table_data'):
        data = main_window_or_data._get_editor_table_data()
    
    # Make sure directory is a string
    if not isinstance(directory, str):
        directory = "."
    
    path = os.path.join(directory, INDEX_FILENAME)
    with open(path, "w", encoding="utf-8") as f:
        for row in data:
            # Convert dict to list if necessary
            if isinstance(row, dict):
                # Define the expected order of fields
                fields = ["include", "executable", "directory", "steam_title", 
                          "name_override", "options", "arguments", "steam_id",
                          "as_admin", "no_tb"]
                row_values = [row.get(field, "") for field in fields]
            else:
                # Assume it's already a list
                row_values = row
            
            # Convert all values to strings
            safe_row = [str(cell).replace(PIPE_CHAR, SAFE_PIPE_CHAR) for cell in row_values]
            f.write(PIPE_CHAR.join(safe_row) + "\n")
    
    # Show a status message if possible
    if hasattr(main_window_or_data, 'statusBar'):
        main_window_or_data.statusBar().showMessage(f"Saved index to {path}", 3000)


def load_index(main_window_or_directory=".", callback=None):
    """
    Load the current.index file and return as a list of lists.
    
    Args:
        main_window_or_directory: Either MainWindow object or directory string
        callback: Optional callback function to process loaded data
    
    Returns:
        A list of lists representing the loaded data
    """
    # Determine if we got a main_window or a directory string
    if hasattr(main_window_or_directory, 'editor_table'):
        main_window = main_window_or_directory
        directory = "."
    else:
        main_window = None
        directory = main_window_or_directory if isinstance(main_window_or_directory, str) else "."
    
    # Find the index file
    path = os.path.join(directory, INDEX_FILENAME)
    if not os.path.exists(path):
        # Try project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        path = os.path.join(project_root, INDEX_FILENAME)
        
        if not os.path.exists(path):
            if main_window and hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Index file not found: {INDEX_FILENAME}", 3000)
            return []
    
    # Load the index file
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Parse each line into a list of fields
        table_data = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(PIPE_CHAR)
            # Replace special pipe char if needed
            for i, part in enumerate(parts):
                parts[i] = part.replace(SAFE_PIPE_CHAR, PIPE_CHAR)
            
            table_data.append(parts)
        
        # If we have a main_window, populate its editor_table
        if main_window and hasattr(main_window, 'editor_table'):
            # Clear existing table
            main_window.editor_table.setRowCount(0)
            
            # Add each row to the table using helper function if available
            if hasattr(main_window, '_add_executable_to_editor_table'):
                for row in table_data:
                    # Ensure we have enough columns
                    if len(row) >= 8:
                        include_checked = row[0].lower() == "true"
                        exec_name = row[1]
                        directory = row[2]
                        steam_name = row[3]
                        name_override = row[4]
                        options = row[5]
                        arguments = row[6]
                        steam_id = row[7]
                        as_admin = row[8].lower() == "true" if len(row) > 8 else False
                        no_tb = row[9].lower() == "true" if len(row) > 9 else False
                        
                        main_window._add_executable_to_editor_table(
                            include_checked, exec_name, directory, steam_name, 
                            name_override, options, arguments, steam_id, as_admin, no_tb
                        )
            else:
                # Fallback in case _add_executable_to_editor_table isn't available
                from Python.ui.game_indexer import add_executable_to_editor_table
                
                for row in table_data:
                    # Ensure we have enough columns
                    if len(row) >= 8:
                        include_checked = row[0].lower() == "true"
                        exec_name = row[1]
                        directory = row[2]
                        steam_name = row[3]
                        name_override = row[4]
                        options = row[5]
                        arguments = row[6]
                        steam_id = row[7]
                        as_admin = row[8].lower() == "true" if len(row) > 8 else False
                        no_tb = row[9].lower() == "true" if len(row) > 9 else False
                        
                        add_executable_to_editor_table(
                            main_window, include_checked, exec_name, directory, steam_name, 
                            name_override, options, arguments, steam_id, as_admin, no_tb
                        )
            
            # Show status message
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Loaded {len(table_data)} entries from {path}", 3000)
        
        # Call callback if provided
        if callback:
            callback(table_data)
        
        return table_data
    
    except Exception as e:
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Error loading index: {e}", 5000)
        print(f"Error loading index {path}: {e}")
        return []


def backup_index(directory="."):
    """
    Backup current.index to index_backups/current.index.0001, .0002, etc.
    """
    src = os.path.join(directory, INDEX_FILENAME)
    if not os.path.exists(src):
        return
    backup_dir = os.path.join(directory, BACKUP_DIR)
    os.makedirs(backup_dir, exist_ok=True)
    # Find next available backup number
    existing = [f for f in os.listdir(backup_dir) if f.startswith(INDEX_FILENAME)]
    nums = [int(f.split(".")[-1]) for f in existing if f.split(".")[-1].isdigit()]
    next_num = max(nums, default=0) + 1
    backup_name = f"{INDEX_FILENAME}.{next_num:04d}"
    dst = os.path.join(backup_dir, backup_name)
    shutil.copy2(src, dst)


def delete_all_indexes(main_window_or_directory="."):
    """
    Delete current.index and all backups.
    
    Args:
        main_window_or_directory: Either MainWindow object or directory string
    """
    # Determine if we got a main_window or a directory string
    if hasattr(main_window_or_directory, 'statusBar'):
        main_window = main_window_or_directory
        directory = "."
    else:
        main_window = None
        directory = main_window_or_directory if isinstance(main_window_or_directory, str) else "."
    
    # Delete the index file
    idx = os.path.join(directory, INDEX_FILENAME)
    if os.path.exists(idx):
        os.remove(idx)
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Deleted index file: {idx}", 3000)
    
    # Delete backup directory and its contents
    backup_dir = os.path.join(directory, BACKUP_DIR)
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            os.remove(os.path.join(backup_dir, f))
        os.rmdir(backup_dir)
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Deleted backup directory: {backup_dir}", 3000)

