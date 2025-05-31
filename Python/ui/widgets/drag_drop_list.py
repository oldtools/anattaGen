"""
Custom drag and drop list widget for reordering items
"""

from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

class DragDropListWidget(QListWidget):
    """A list widget that supports drag and drop for reordering items"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        # Set minimum size
        self.setMinimumHeight(150)
        
    def dropEvent(self, event):
        """Override drop event to handle reordering"""
        super().dropEvent(event)
        # Emit a signal or perform any additional actions after drop
        self.model().layoutChanged.emit()