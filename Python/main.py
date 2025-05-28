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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyle("fusion")    
    window.show()
    sys.exit(app.exec()) 
