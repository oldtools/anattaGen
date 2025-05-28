from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QMenu, QFileDialog
)
from PyQt6.QtCore import Qt

def create_editor_tab_item_status_widget(parent, initial_text="", row=-1, col=-1, data_key=None):
    """Create a widget containing a checkbox for table cells
    
    Args:
        parent: The parent window/widget
        initial_text: Initial state as text ("true"/"false")
        row, col: Row and column for callback purposes
        data_key: Optional data key for callback data
        
    Returns:
        A widget containing a checkbox with proper state
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    # Create checkbox
    check = QCheckBox()
    check.setChecked(str(initial_text).lower() == "true")
    layout.addWidget(check, 0, Qt.AlignmentFlag.AlignCenter)
    
    # Connect to parent's edited handler if available
    if hasattr(parent, '_on_editor_table_edited'):
        check.stateChanged.connect(lambda state: parent._on_editor_table_edited(QTableWidgetItem()))
    
    return widget

def populate_editor_tab(main_window):
    """Populate the editor tab with all required UI elements"""
    # Create main layout for the editor tab
    main_window.editor_tab_layout = QVBoxLayout(main_window.editor_tab)
    
    # Create button layout
    button_layout = QHBoxLayout()
    
    # Create index management button with dropdown menu
    main_window.index_button = QPushButton("Index")
    index_menu = QMenu(main_window.index_button)
    
    # Add actions to the menu
    load_action = index_menu.addAction("Load Index")
    load_action.triggered.connect(main_window._load_index)
    
    save_action = index_menu.addAction("Save Index")
    save_action.triggered.connect(main_window._save_editor_table_to_index)
    
    delete_action = index_menu.addAction("Delete Indexes")
    delete_action.triggered.connect(main_window._on_delete_indexes)
    
    main_window.index_button.setMenu(index_menu)
    button_layout.addWidget(main_window.index_button)
    
    # Add clear list view button
    main_window.clear_listview_button = QPushButton("Clear List-View")
    main_window.clear_listview_button.clicked.connect(main_window._on_clear_listview)
    button_layout.addWidget(main_window.clear_listview_button)
    
    # Add regenerate names button
    regenerate_names_button = QPushButton("Regenerate All Names")
    regenerate_names_button.clicked.connect(main_window._regenerate_all_names)
    regenerate_names_button.setToolTip("Regenerate all name overrides in the table")
    button_layout.addWidget(regenerate_names_button)
    
    # Add spacer to push CREATE button to the right
    button_layout.addStretch(1)
    
    # Add CREATE button aligned to the right
    create_button = QPushButton("CREATE")
    create_button.setStyleSheet("font-weight: bold;")
    create_button.setToolTip("Generate and create profiles with configurations reflected by values in the list-view")
    # TODO: Connect this button to the profile creation functionality
    button_layout.addWidget(create_button)
    
    main_window.editor_tab_layout.addLayout(button_layout)
    
    # Create table for editing entries
    main_window.editor_table = QTableWidget()
    main_window.editor_table.setColumnCount(24)
    main_window.editor_table.setHorizontalHeaderLabels([
        "Include", "Executable", "Directory", "Steam Title", 
        "Name Override", "Options", "Args", "Steam ID",
        "P1 Profile", "P2 Profile", "Desktop CTRL", 
        "Game Monitor CFG", "Desktop Monitor CFG", 
        "Post 1", "Post 2", "Post 3", 
        "Pre 1", "Pre 2", "Pre 3", 
        "Just After", "Just Before", "Borderless", 
        "AsAdmin", "NoTB"
    ])
    
    # Set column properties
    main_window.editor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    main_window.editor_table.horizontalHeader().setStretchLastSection(True)
    main_window.editor_table.verticalHeader().setVisible(False)
    
    # Connect signals
    main_window.editor_table.cellClicked.connect(main_window._on_editor_table_cell_left_click)
    main_window.editor_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    main_window.editor_table.customContextMenuRequested.connect(main_window._on_editor_table_custom_context_menu)
    main_window.editor_table.horizontalHeader().sectionClicked.connect(main_window._on_editor_table_header_click)
    
    main_window.editor_tab_layout.addWidget(main_window.editor_table) 
