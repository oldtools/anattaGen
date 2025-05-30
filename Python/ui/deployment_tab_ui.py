# Python/ui/deployment_tab_ui.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QGroupBox, QFormLayout, QListWidget, QAbstractItemView,
    QPushButton, QFrame, QSplitter, QLineEdit
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor

class DragDropListWidget(QListWidget):
    """Custom QListWidget that supports drag and drop reordering"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #aaa;
                border-radius: 4px;
                background-color: #f8f8f8;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
    
    def startDrag(self, supportedActions):
        """Custom drag start to show a better drag visual"""
        item = self.currentItem()
        if not item:
            return
            
        # Create mime data
        mimeData = QMimeData()
        mimeData.setText(item.text())
        
        # Create drag object
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        
        # Create a pixmap for the drag visual
        pixmap = QPixmap(self.viewport().size())
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Paint the item onto the pixmap
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)
        painter.fillRect(self.visualItemRect(item), QColor(200, 200, 255))
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(self.visualItemRect(item), Qt.AlignmentFlag.AlignCenter, item.text())
        painter.end()
        
        # Set the drag pixmap
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.viewport().mapFromGlobal(self.cursor().pos()))
        
        # Execute the drag
        drag.exec(supportedActions)

def populate_deployment_tab(main_window):
    """Populate the deployment tab with UI elements"""
    # Clear the existing layout if it has any widgets
    if hasattr(main_window, 'deployment_tab_layout'):
        # Remove all widgets from the layout
        while main_window.deployment_tab_layout.count():
            item = main_window.deployment_tab_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    else:
        # Create the layout if it doesn't exist
        main_window.deployment_tab_layout = QVBoxLayout(main_window.deployment_tab)
    
    # Create a main layout for the deployment tab content
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    # --- Top section for general options ---
    general_options_group_box = QGroupBox("General Options")
    general_options_layout = QVBoxLayout(general_options_group_box)
    
    # Create checkboxes for general options
    main_window.net_check_checkbox = QCheckBox("Check Network Connection")
    main_window.net_check_checkbox.setToolTip("If checked, the launcher will check for an active network connection before launching the game.")
    
    main_window.name_check_checkbox = QCheckBox("Check Game Name")
    main_window.name_check_checkbox.setToolTip("If checked, the launcher will verify the game name before launching.")
    
    main_window.use_kill_list_checkbox = QCheckBox("Use Kill List")
    main_window.use_kill_list_checkbox.setToolTip("If checked, the launcher will kill processes in the kill list before launching the game.")
    
    main_window.run_as_admin_checkbox = QCheckBox("Run as Administrator")
    main_window.run_as_admin_checkbox.setToolTip("If checked, the launcher will run the game as administrator.")
    
    main_window.hide_taskbar_checkbox = QCheckBox("Hide Taskbar")
    main_window.hide_taskbar_checkbox.setToolTip("If checked, the taskbar will be hidden when the game is running.")
    
    main_window.enable_launcher_checkbox = QCheckBox("Enable Launcher")
    main_window.enable_launcher_checkbox.setToolTip("If checked, the launcher will be enabled for this game.")
    
    main_window.apply_mapper_profiles_checkbox = QCheckBox("Apply Mapper Profiles")
    main_window.apply_mapper_profiles_checkbox.setToolTip("If checked, the launcher will apply controller mapper profiles.")
    
    main_window.enable_borderless_windowing_checkbox = QCheckBox("Enable Borderless Windowing")
    main_window.enable_borderless_windowing_checkbox.setToolTip("If checked, the launcher will enable borderless windowing for the game.")
    
    main_window.terminate_bw_on_exit_checkbox = QCheckBox("Terminate Borderless on Exit")
    main_window.terminate_bw_on_exit_checkbox.setToolTip("If checked, the launcher will terminate the borderless windowing application when the game exits.")
    
    # Create a layout for the checkboxes in two columns
    general_options_columns_layout = QHBoxLayout()
    
    column1_layout = QVBoxLayout()
    column1_layout.addWidget(main_window.run_as_admin_checkbox)
    column1_layout.addWidget(main_window.hide_taskbar_checkbox)
    column1_layout.addWidget(main_window.enable_launcher_checkbox)
    column1_layout.addWidget(main_window.apply_mapper_profiles_checkbox)
    column1_layout.addWidget(main_window.enable_borderless_windowing_checkbox)
    column1_layout.addWidget(main_window.terminate_bw_on_exit_checkbox)
    column1_layout.addStretch(1)
    
    column2_layout = QVBoxLayout()
    column2_layout.addWidget(main_window.net_check_checkbox)
    column2_layout.addWidget(main_window.name_check_checkbox)
    column2_layout.addWidget(main_window.use_kill_list_checkbox)
    column2_layout.addStretch(1)

    general_options_columns_layout.addLayout(column1_layout)
    general_options_columns_layout.addLayout(column2_layout)
    
    general_options_layout.addLayout(general_options_columns_layout)
    main_layout.addWidget(general_options_group_box)

    # --- Middle section for path configurations ---
    middle_section_form_layout = QFormLayout()
    middle_section_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
    
    path_details_label = QLabel("<b>Application & Profile Paths (from Setup Tab):</b>")
    middle_section_form_layout.addRow(path_details_label)
    
    # These attributes are expected to be set on main_window by populate_setup_tab
    paths_to_display = [
        ("Player 1 Profile File:", main_window.p1_profile_edit if hasattr(main_window, 'p1_profile_edit') else None),
        ("Player 2 Profile File:", main_window.p2_profile_edit if hasattr(main_window, 'p2_profile_edit') else None),
        ("Media Center/Desktop Profile File:", main_window.mediacenter_profile_edit if hasattr(main_window, 'mediacenter_profile_edit') else None),
        ("MM Gaming Config File:", main_window.multimonitor_gaming_config_edit if hasattr(main_window, 'multimonitor_gaming_config_edit') else None),
        ("MM Media/Desktop Config File:", main_window.multimonitor_media_config_edit if hasattr(main_window, 'multimonitor_media_config_edit') else None),
        ("Controller Mapper App:", main_window.controller_mapper_app_line_edit if hasattr(main_window, 'controller_mapper_app_line_edit') else None),
        ("Borderless Windowing App:", main_window.borderless_app_line_edit if hasattr(main_window, 'borderless_app_line_edit') else None),
        ("Multi-Monitor App:", main_window.multimonitor_app_line_edit if hasattr(main_window, 'multimonitor_app_line_edit') else None),
        ("Just After Launch App:", main_window.after_launch_app_line_edit if hasattr(main_window, 'after_launch_app_line_edit') else None),
        ("Just Before Exit App:", main_window.before_exit_app_line_edit if hasattr(main_window, 'before_exit_app_line_edit') else None),
    ]
    
    # Add pre-launch apps
    if hasattr(main_window, 'pre_launch_app_line_edits'):
        for i, le in enumerate(main_window.pre_launch_app_line_edits):
            paths_to_display.append((f"Pre-Launch App {i+1}:", le))
    
    # Add post-launch apps
    if hasattr(main_window, 'post_launch_app_line_edits'):
        for i, le in enumerate(main_window.post_launch_app_line_edits):
            paths_to_display.append((f"Post-Launch App {i+1}:", le))
            
    # Create a dictionary to store the deployment path options
    main_window.deployment_path_options = {}
    
    for label_text, setup_qlineedit in paths_to_display:
        if setup_qlineedit:
            # Use the imported function create_deployment_path_row_widget
            # It expects parent_window (main_window) and the QLineEdit to mirror
            from .ui_widgets import create_deployment_path_row_widget
            path_row_container_widget, uoc_radio, path_label, lc_radio = create_deployment_path_row_widget(main_window, setup_qlineedit)
            middle_section_form_layout.addRow(label_text, path_row_container_widget)
            
            # Store the radio button group for this path
            key = setup_qlineedit.objectName()
            if key:
                from PyQt6.QtWidgets import QButtonGroup
                radio_group = QButtonGroup(main_window)
                radio_group.addButton(uoc_radio)
                radio_group.addButton(lc_radio)
                main_window.deployment_path_options[key] = radio_group
        else:
             middle_section_form_layout.addRow(label_text, QLabel("<i>Path not configured in Setup Tab</i>"))
    
    main_layout.addLayout(middle_section_form_layout)
    
    # --- Add the launch sequence and exit sequence lists ---
    sequence_layout = QHBoxLayout()
    
    # Create a splitter to allow resizing
    splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Launch sequence group
    launch_sequence_group = QGroupBox("Launch Sequence")
    launch_sequence_layout = QVBoxLayout(launch_sequence_group)
    
    # Create the launch sequence list
    main_window.launch_sequence_list = DragDropListWidget()
    main_window.launch_sequence_list.addItems([
        "Controller-Mapper", 
        "Monitor-Config", 
        "No-TB", 
        "Pre1", 
        "Pre2", 
        "Pre3", 
        "Borderless"
    ])
    
    # Add buttons to manage the launch sequence
    launch_buttons_layout = QHBoxLayout()
    reset_launch_btn = QPushButton("Reset")
    reset_launch_btn.clicked.connect(lambda: reset_launch_sequence(main_window))
    launch_buttons_layout.addWidget(reset_launch_btn)
    launch_buttons_layout.addStretch(1)
    
    launch_sequence_layout.addWidget(QLabel("Drag to reorder:"))
    launch_sequence_layout.addWidget(main_window.launch_sequence_list)
    launch_sequence_layout.addLayout(launch_buttons_layout)
    
    # Exit sequence group
    exit_sequence_group = QGroupBox("Exit Sequence")
    exit_sequence_layout = QVBoxLayout(exit_sequence_group)
    
    # Create the exit sequence list
    main_window.exit_sequence_list = DragDropListWidget()
    main_window.exit_sequence_list.addItems([
        "Post1", 
        "Post2", 
        "Post3", 
        "Monitor-Config", 
        "Taskbar",
        "Controller-Mapper"  # Added Controller-Mapper to exit sequence
    ])
    
    # Add buttons to manage the exit sequence
    exit_buttons_layout = QHBoxLayout()
    reset_exit_btn = QPushButton("Reset")
    reset_exit_btn.clicked.connect(lambda: reset_exit_sequence(main_window))
    exit_buttons_layout.addWidget(reset_exit_btn)
    exit_buttons_layout.addStretch(1)
    
    exit_sequence_layout.addWidget(QLabel("Drag to reorder:"))
    exit_sequence_layout.addWidget(main_window.exit_sequence_list)
    exit_sequence_layout.addLayout(exit_buttons_layout)
    
    # Add the groups to the splitter
    splitter.addWidget(launch_sequence_group)
    splitter.addWidget(exit_sequence_group)
    
    # Add the splitter to the sequence layout
    sequence_layout.addWidget(splitter)
    
    # Add the sequence layout to the main layout
    main_layout.addLayout(sequence_layout)
    
    # Add a horizontal line separator
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    main_layout.addWidget(line)
    
    # --- Bottom section for creation options ---
    creation_options_group_box = QGroupBox("Creation Options")
    creation_options_layout = QVBoxLayout(creation_options_group_box)
    
    # Create checkboxes for creation options
    main_window.create_overwrite_launcher_checkbox = QCheckBox("Create/Overwrite Launcher")
    main_window.create_overwrite_launcher_checkbox.setToolTip("If checked, the launcher will be created or overwritten.")
    main_window.create_overwrite_launcher_checkbox.setChecked(True)
    
    main_window.create_profile_folders_checkbox = QCheckBox("Create Profile Folders")
    main_window.create_profile_folders_checkbox.setToolTip("If checked, profile folders will be created.")
    main_window.create_profile_folders_checkbox.setChecked(True)
    
    main_window.create_overwrite_joystick_profiles_checkbox = QCheckBox("Create/Overwrite Joystick Profiles")
    main_window.create_overwrite_joystick_profiles_checkbox.setToolTip("If checked, joystick profiles will be created or overwritten.")
    
    # Add the checkboxes to the layout
    creation_options_layout.addWidget(main_window.create_overwrite_launcher_checkbox)
    creation_options_layout.addWidget(main_window.create_profile_folders_checkbox)
    creation_options_layout.addWidget(main_window.create_overwrite_joystick_profiles_checkbox)
    
    # Add the creation options group box to the main layout
    main_layout.addWidget(creation_options_group_box)
    
    # Add the main layout to the deployment tab layout
    main_window.deployment_tab_layout.addLayout(main_layout)
    
    # Print debug info
    print("Deployment tab populated successfully")

def reset_launch_sequence(main_window):
    """Reset the launch sequence to default"""
    main_window.launch_sequence_list.clear()
    main_window.launch_sequence_list.addItems([
        "Controller-Mapper", 
        "Monitor-Config", 
        "No-TB", 
        "Pre1", 
        "Pre2", 
        "Pre3", 
        "Borderless"
    ])

def reset_exit_sequence(main_window):
    """Reset the exit sequence to default"""
    main_window.exit_sequence_list.clear()
    main_window.exit_sequence_list.addItems([
        "Post1", 
        "Post2", 
        "Post3", 
        "Monitor-Config", 
        "Taskbar",
        "Controller-Mapper"  # Added Controller-Mapper to exit sequence
    ])

def print_deployment_options(main_window):
    """Print the deployment_path_options for debugging"""
    if hasattr(main_window, 'deployment_path_options'):
        print(f"Found {len(main_window.deployment_path_options)} deployment path options:")
        for path_key, radio_group in main_window.deployment_path_options.items():
            checked_button = radio_group.checkedButton()
            if checked_button:
                mode = checked_button.text()
                print(f"  {path_key}_mode = {mode}")
            else:
                print(f"  {path_key} has no checked button")
    else:
        print("No deployment_path_options found on main_window")

def create_deployment_path_row_widget(parent_window, setup_qlineedit_to_mirror: QLineEdit):
    """Create a row widget with UOC/LC radio buttons and a path label"""
    row_widget = QWidget()
    row_layout = QHBoxLayout(row_widget)
    row_layout.setContentsMargins(0, 0, 0, 0)

    # Create radio button group
    radio_group = QButtonGroup(row_widget)
    
    # Replace checkboxes with radio buttons
    uoc_radio = QRadioButton("UOC")
    uoc_radio.setToolTip("Use Original Config: If selected, the application will use the path defined in the Setup tab.")
    uoc_radio.setChecked(True)
    
    lc_radio = QRadioButton("LC")
    lc_radio.setToolTip("Launch Conditionally: If selected, this associated application/script will only be launched if certain conditions are met (details TBD).")
    
    # Add radio buttons to the group
    radio_group.addButton(uoc_radio)
    radio_group.addButton(lc_radio)
    
    # Add radio buttons to the layout
    row_layout.addWidget(uoc_radio)
    row_layout.addWidget(lc_radio)
    
    # Add a label showing the path from the setup tab
    path_label = QLabel(setup_qlineedit_to_mirror.text())
    path_label.setStyleSheet("color: gray;")
    row_layout.addWidget(path_label, 1)  # Give the label a stretch factor of 1
    
    # Connect the setup_qlineedit's textChanged signal to update the path_label
    setup_qlineedit_to_mirror.textChanged.connect(path_label.setText)
    
    # Get the object name or generate a unique key
    key = setup_qlineedit_to_mirror.objectName()
    
    # If no object name, try to find the attribute name
    if not key:
        for attr_name in dir(parent_window):
            if getattr(parent_window, attr_name, None) is setup_qlineedit_to_mirror:
                key = attr_name
                break
    
    # If still no key, use a generic name with the id
    if not key:
        key = f"path_{id(setup_qlineedit_to_mirror)}"
    
    # Ensure parent_window has deployment_path_options
    if not hasattr(parent_window, 'deployment_path_options'):
        parent_window.deployment_path_options = {}
    
    # Store the radio group in the parent_window for later access
    parent_window.deployment_path_options[key] = radio_group
    print(f"Added deployment path option: {key}")
    
    # Connect radio buttons to save config when changed
    from Python.ui.config_manager import save_configuration
    uoc_radio.toggled.connect(lambda checked, pw=parent_window: save_configuration(pw) if checked else None)
    lc_radio.toggled.connect(lambda checked, pw=parent_window: save_configuration(pw) if checked else None)
    
    return row_widget, radio_group, uoc_radio, lc_radio
