"""
Handles file propagation for game profiles
This functionality has been consolidated into creation_controller.py
"""

import os
import shutil
from PyQt6.QtCore import QCoreApplication

class FilePropagator:
    """Handles file propagation for game profiles"""
    
    def __init__(self, main_window):
        """Initialize with the main window reference"""
        self.main_window = main_window
        self.max_file_size = 10 * 1024 * 1024  # 10 MB
    
    def propagate_files(self, game_data, profile_folder_path):
        """
        Propagate files to the profile folder
        This is a stub - functionality moved to CreationController._propagate_files
        """
        print("FilePropagator.propagate_files is deprecated. Use CreationController._propagate_files instead.")
        return 0
    
    def _get_paths_to_propagate(self, game_data):
        """
        Get the paths to propagate from the game data
        This is a stub - functionality moved to CreationController._get_paths_to_propagate
        """
        print("FilePropagator._get_paths_to_propagate is deprecated. Use CreationController._get_paths_to_propagate instead.")
        return []
    
    def _replace_variables(self, path, game_data):
        """
        Replace variables in the path with values from game_data
        This is a stub - functionality moved to CreationController._replace_variables
        """
        print("FilePropagator._replace_variables is deprecated. Use CreationController._replace_variables instead.")
        return path


