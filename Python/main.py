import sys
import os
import logging

# Add the parent directory ([RJ_PROJ])to sys.path to allow relative imports
# when running this script directly.
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Set up logging to file
log_file = os.path.join(script_dir, 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Log startup information
logging.info(f"Starting application from {script_dir}")
logging.info(f"Log file: {os.path.abspath(log_file)}")

from PyQt6.QtWidgets import QApplication
from Python.main_window_new import MainWindow
from Python.ui.creation.creation_controller import CreationController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyle("Material")    
    window.show()
    sys.exit(app.exec()) 

# Add this import at the top of the file
from Python.ui.creation.creation_controller import CreationController

# Inside the MainWindow class initialization or setup method
def setup_controllers(self):
    """Initialize all controllers"""
    # Initialize the creation controller
    self.creation_controller = CreationController(self)
    
    # Connect the Create button to the creation process
    if hasattr(self, 'create_button'):
        self.create_button.clicked.connect(self.start_creation_process)

def start_creation_process(self):
    """Start the creation process for selected games"""
    self.creation_controller.create_all()
