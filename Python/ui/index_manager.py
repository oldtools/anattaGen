import os
import shutil
from datetime import datetime

INDEX_FILENAME = "current.index"
BACKUP_DIR = "index_backups"
PIPE_CHAR = "|"
SAFE_PIPE_CHAR = ""  # U+2502


def save_index(main_window, directory, data):
    """Save index data to a file"""
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Create a backup of the current index if it exists
    backup_index(directory)
    
    # Save the index
    path = os.path.join(directory, INDEX_FILENAME)
    with open(path, "w", encoding="utf-8") as f:
        for row in data:
            # Convert dict to list if necessary
            if isinstance(row, dict):
                # Define the expected order of fields
                fields = ["include", "executable", "directory", "steam_title", 
                          "name_override", "options", "arguments", "steam_id",
                          "p1_profile", "p2_profile", "desktop_ctrl", 
                          "game_monitor_cfg", "desktop_monitor_cfg", 
                          "post1", "post2", "post3", 
                          "pre1", "pre2", "pre3", 
                          "just_after", "just_before", "borderless",
                          "as_admin", "no_tb"]
                
                # Get path indicators
                path_indicators = row.get("path_indicators", {})
                
                # Create a list of values
                row_values = []
                for i, field in enumerate(fields):
                    if 8 <= i <= 20:  # Path fields (columns 8-20)
                        # Use the indicator from path_indicators if available
                        col = i
                        indicator = path_indicators.get(f"col_{col}_indicator", "<")  # Default to CEN
                        # If no indicator, use the value from the field
                        if f"col_{col}_indicator" not in path_indicators and field in row:
                            indicator = row[field]
                        # If still no indicator, default to CEN
                        if not indicator:
                            indicator = "<"
                        row_values.append(indicator)
                    else:
                        row_values.append(row.get(field, ""))
            else:
                # Assume it's already a list
                row_values = row
            
            # Convert all values to strings
            safe_row = [str(cell).replace(PIPE_CHAR, SAFE_PIPE_CHAR) for cell in row_values]
            f.write(PIPE_CHAR.join(safe_row) + "\n")
    
    # Show a status message if possible
    if main_window and hasattr(main_window, 'statusBar'):
        main_window.statusBar().showMessage(f"Saved index to {path}", 3000)


def load_index(main_window=None, directory=None):
    """
    Load the index file and return the data as a list of dictionaries.
    
    Args:
        main_window: Optional MainWindow object to update status bar
        directory: Directory to load the index file from (default: app root)
    
    Returns:
        List of dictionaries with game data
    """
    # Get the app's root directory if directory is not specified
    if directory is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        directory = os.path.dirname(os.path.dirname(script_dir))
    
    # Find the index file
    path = os.path.join(directory, INDEX_FILENAME)
    if not os.path.exists(path):
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Index file not found: {INDEX_FILENAME}", 3000)
        return []
    
    # Load the data
    data = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    # Replace safe pipe char back to normal pipe if needed
                    parts = line.strip().split(PIPE_CHAR)
                    parts = [p.replace(SAFE_PIPE_CHAR, PIPE_CHAR) if SAFE_PIPE_CHAR else p for p in parts]
                    
                    # Convert to dictionary
                    row = {
                        "include": parts[0].lower() == "true" if len(parts) > 0 else False,
                        "executable": parts[1] if len(parts) > 1 else "",
                        "directory": parts[2] if len(parts) > 2 else "",
                        "steam_title": parts[3] if len(parts) > 3 else "",
                        "name_override": parts[4] if len(parts) > 4 else "",
                        "options": parts[5] if len(parts) > 5 else "",
                        "arguments": parts[6] if len(parts) > 6 else "",
                        "steam_id": parts[7] if len(parts) > 7 else "",
                        "as_admin": parts[8].lower() == "true" if len(parts) > 8 else False,
                        "no_tb": parts[9].lower() == "true" if len(parts) > 9 else False
                    }
                    data.append(row)
        
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Loaded {len(data)} entries from {path}", 3000)
    except Exception as e:
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"Error loading index: {str(e)}", 3000)
        print(f"Error loading index: {e}")
    
    return data


def backup_index(directory=None):
    """
    Backup current.index to index_backups/current.index.0001, .0002, etc.
    """
    # Get the app's root directory if directory is not specified
    if directory is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        directory = os.path.dirname(os.path.dirname(script_dir))
    
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

