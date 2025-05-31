# Python/ui/deployment_tab_ui.py
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QWidget, QSplitter,
    QButtonGroup, QRadioButton, QMessageBox, QTabWidget, QMenu
)
from PyQt6.QtCore import Qt
from .ui_widgets import create_deployment_path_row_widget
from .widgets import DragDropListWidget

def populate_deployment_tab(main_window):
    """Populate the deployment tab with UI elements"""
    from PyQt6.QtWidgets import (
        QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
        QPushButton, QFileDialog, QWidget, QGroupBox, QCheckBox,
        QSplitter, QButtonGroup, QRadioButton, QMenu, QTableWidget
    )
    from PyQt6.QtCore import Qt
    from .ui_widgets import create_deployment_path_row_widget
    from .widgets import DragDropListWidget
    from .accordion import AccordionSection
    
    # Create the deployment tab layout
    main_window.deployment_tab_layout = QVBoxLayout(main_window.deployment_tab)
    
    # Create a main layout for the deployment tab content
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    # --- Section 1: General Options ---
    general_options_widget = QWidget()
    general_options_layout = QVBoxLayout(general_options_widget)
    
    # Create checkboxes for general options
    main_window.net_check_checkbox = QCheckBox("Check Network Connection")
    main_window.net_check_checkbox.setToolTip("If checked, the launcher will check for an active network connection before launching the game.")
    
    # Create Steam DB button with dropdown menu
    steam_db_button = QPushButton("STEAM DB")
    steam_db_button.setToolTip("Steam database operations")
    steam_db_button.setStyleSheet("QPushButton { min-width: 144px; }")
    
    # Create a menu for the Steam DB button
    steam_db_menu = QMenu()
    update_steam_action = steam_db_menu.addAction("Update steam.json")
    update_steam_action.triggered.connect(main_window._update_steam_json_cache)
    delete_json_action = steam_db_menu.addAction("Delete steam.json")
    delete_json_action.triggered.connect(main_window._delete_steam_json)
    
    # Set the menu for the button
    steam_db_button.setMenu(steam_db_menu)
    
    # Create a layout for the net check and Steam DB button
    net_check_layout = QHBoxLayout()
    net_check_layout.addWidget(main_window.net_check_checkbox)
    net_check_layout.addWidget(steam_db_button)
    net_check_layout.addStretch(1)
    
    main_window.name_check_checkbox = QCheckBox("Check Game Name")
    main_window.name_check_checkbox.setToolTip("If checked, the launcher will verify the game name before launching. Also enables name-matching during indexing.")
    
    main_window.hide_taskbar_checkbox = QCheckBox("Hide Taskbar")
    main_window.hide_taskbar_checkbox.setToolTip("If checked, the launcher will hide the taskbar when the game launches.")
    
    main_window.enable_launcher_checkbox = QCheckBox("Enable Launcher")
    main_window.enable_launcher_checkbox.setToolTip("If checked, the launcher will be enabled.")
    
    main_window.apply_mapper_profiles_checkbox = QCheckBox("Apply Mapper Profiles")
    main_window.apply_mapper_profiles_checkbox.setToolTip("If checked, the launcher will apply controller mapper profiles.")
    
    main_window.enable_borderless_windowing_checkbox = QCheckBox("Enable Borderless Windowing")
    main_window.enable_borderless_windowing_checkbox.setToolTip("If checked, the launcher will enable borderless windowing for the game.")
    
    main_window.terminate_bw_on_exit_checkbox = QCheckBox("Terminate Borderless on Exit")
    main_window.terminate_bw_on_exit_checkbox.setToolTip("If checked, the launcher will terminate the borderless windowing application when the game exits.")
    
    # Create a layout for the checkboxes in two columns
    general_options_columns_layout = QHBoxLayout()
    
    column1_layout = QVBoxLayout()
    column1_layout.addLayout(net_check_layout)  # Add the net check layout with Steam DB button
    column1_layout.addWidget(main_window.name_check_checkbox)
    column1_layout.addStretch(1)
    
    column2_layout = QVBoxLayout()
    column2_layout.addWidget(main_window.hide_taskbar_checkbox)
    column2_layout.addWidget(main_window.enable_launcher_checkbox)
    column2_layout.addWidget(main_window.apply_mapper_profiles_checkbox)
    column2_layout.addStretch(1)
    
    column3_layout = QVBoxLayout()
    column3_layout.addWidget(main_window.enable_borderless_windowing_checkbox)
    column3_layout.addWidget(main_window.terminate_bw_on_exit_checkbox)
    column3_layout.addStretch(1)
    
    general_options_columns_layout.addLayout(column1_layout)
    general_options_columns_layout.addLayout(column2_layout)
    general_options_columns_layout.addLayout(column3_layout)
    
    general_options_layout.addLayout(general_options_columns_layout)
    
    # --- Section 2: Path Configurations ---
    path_config_widget = QWidget()
    path_config_layout = QFormLayout(path_config_widget)
    
    path_details_label = QLabel("<b>Application & Profile Paths (from Setup Tab):</b>")
    path_config_layout.addRow(path_details_label)
    
    # These attributes are expected to be set on main_window by populate_setup_tab
    paths_to_display = [
        ("Player 1 Profile File:", main_window.p1_profile_edit if hasattr(main_window, 'p1_profile_edit') else None),
        ("Player 2 Profile File:", main_window.p2_profile_edit if hasattr(main_window, 'p2_profile_edit') else None),
        ("Media Center/Desktop Profile File:", main_window.mediacenter_profile_edit if hasattr(main_window, 'mediacenter_profile_edit') else None),
        ("MM Gaming Config File:", main_window.multimonitor_gaming_config_edit if hasattr(main_window, 'multimonitor_gaming_config_edit') else None),
        ("MM Media/Desktop Config File:", main_window.multimonitor_media_config_edit if hasattr(main_window, 'multimonitor_media_config_edit') else None),
    ]
    
    # Initialize the deployment path options dictionary if it doesn't exist
    if not hasattr(main_window, 'deployment_path_options'):
        main_window.deployment_path_options = {}
    
    for label_text, setup_qlineedit in paths_to_display:
        if setup_qlineedit:
            try:
                # Create a container widget for the row
                path_row_container_widget = QWidget()
                path_row_layout = QHBoxLayout(path_row_container_widget)
                path_row_layout.setContentsMargins(0, 0, 0, 0)
                
                # Create radio buttons
                uoc_radio = QRadioButton("CEN")
                uoc_radio.setToolTip("Use Original Config: If selected, the application will use the path defined in the Setup tab.")
                uoc_radio.setChecked(True)
                
                lc_radio = QRadioButton("LC")
                lc_radio.setToolTip("Launch Conditionally: If selected, this associated application/script will only be launched if certain conditions are met (details TBD).")
                
                # Create a button group
                radio_group = QButtonGroup(path_row_container_widget)
                radio_group.addButton(uoc_radio)
                radio_group.addButton(lc_radio)
                
                # Create a path display label
                path_display = QLineEdit()
                path_display.setText(setup_qlineedit.text())
                path_display.setReadOnly(True)
                
                # Connect the setup line edit to update the path display
                setup_qlineedit.textChanged.connect(lambda text, display=path_display: display.setText(text))
                
                # Add widgets to the layout
                path_row_layout.addWidget(uoc_radio)
                path_row_layout.addWidget(path_display, 1)
                path_row_layout.addWidget(lc_radio)
                
                # Store the radio group in the deployment_path_options dictionary
                path_key = setup_qlineedit.objectName()
                if path_key:
                    main_window.deployment_path_options[path_key] = radio_group
                
                # Add the row to the form layout
                path_config_layout.addRow(label_text, path_row_container_widget)
            except Exception as e:
                print(f"Error creating path row for {label_text}: {e}")
    
    # --- Section 3: Sequences and Creation Options ---
    sequences_widget = QWidget()
    sequences_layout = QVBoxLayout(sequences_widget)
    
    # Create a splitter to allow resizing
    splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Launch sequence group
    launch_sequence_group = QGroupBox("Launch Sequence")
    launch_sequence_layout = QVBoxLayout(launch_sequence_group)
    
    # Create the launch sequence list with improved styling
    main_window.launch_sequence_list = DragDropListWidget()
    main_window.launch_sequence_list.setToolTip("Drag items to reorder the launch sequence. This determines the order in which components are started before the game launches.")
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
    reset_launch_btn.setToolTip("Reset the launch sequence to default order")
    reset_launch_btn.clicked.connect(lambda: reset_launch_sequence(main_window))
    launch_buttons_layout.addWidget(reset_launch_btn)
    launch_buttons_layout.addStretch(1)
    
    launch_sequence_layout.addWidget(QLabel("Drag to reorder:"))
    launch_sequence_layout.addWidget(main_window.launch_sequence_list)
    launch_sequence_layout.addLayout(launch_buttons_layout)
    
    # Exit sequence group
    exit_sequence_group = QGroupBox("Exit Sequence")
    exit_sequence_layout = QVBoxLayout(exit_sequence_group)
    
    # Create the exit sequence list with improved styling
    main_window.exit_sequence_list = DragDropListWidget()
    main_window.exit_sequence_list.setToolTip("Drag items to reorder the exit sequence. This determines the order in which components are stopped after the game exits.")
    main_window.exit_sequence_list.addItems([
        "Post1", 
        "Post2", 
        "Post3", 
        "Monitor-Config", 
        "Taskbar",
        "Controller-Mapper"
    ])
    
    # Add buttons to manage the exit sequence
    exit_buttons_layout = QHBoxLayout()
    reset_exit_btn = QPushButton("Reset")
    reset_exit_btn.setToolTip("Reset the exit sequence to default order")
    reset_exit_btn.clicked.connect(lambda: reset_exit_sequence(main_window))
    exit_buttons_layout.addWidget(reset_exit_btn)
    exit_buttons_layout.addStretch(1)
    
    exit_sequence_layout.addWidget(QLabel("Drag to reorder:"))
    exit_sequence_layout.addWidget(main_window.exit_sequence_list)
    exit_sequence_layout.addLayout(exit_buttons_layout)
    
    # --- Creation Options (moved next to exit sequence) ---
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

    # Add Index Sources button
    index_sources_button = QPushButton("Index Sources")
    index_sources_button.clicked.connect(main_window._index_sources)
    index_sources_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")
    creation_options_layout.addWidget(index_sources_button)
    
    # Add Create button
    create_button = QPushButton("Create Selected")
    create_button.clicked.connect(main_window._on_create_button_clicked)
    create_button.setStyleSheet("QPushButton { font-weight: bold; background-color: #4CAF50; color: white; padding: 8px; }")
    creation_options_layout.addWidget(create_button)
    
    # Add the groups to the splitter
    splitter.addWidget(launch_sequence_group)
    splitter.addWidget(exit_sequence_group)
    splitter.addWidget(creation_options_group_box)
    
    # Add the splitter to the sequence layout
    sequences_layout.addWidget(splitter)
    
    # Create accordion sections
    general_options_section = AccordionSection("General Options", general_options_widget)
    path_config_section = AccordionSection("Path Configurations", path_config_widget)
    sequences_section = AccordionSection("Sequences and Creation", sequences_widget)
    
    # Add sections to main layout
    main_layout.addWidget(general_options_section)
    main_layout.addWidget(path_config_section)
    main_layout.addWidget(sequences_section)
    main_layout.addStretch(1)
    
    # Set object names for config saving/loading
    main_window.net_check_checkbox.setObjectName("net_check_checkbox")
    main_window.name_check_checkbox.setObjectName("name_check_checkbox")
    main_window.hide_taskbar_checkbox.setObjectName("hide_taskbar_checkbox")
    main_window.enable_launcher_checkbox.setObjectName("enable_launcher_checkbox")
    main_window.apply_mapper_profiles_checkbox.setObjectName("apply_mapper_profiles_checkbox")
    main_window.enable_borderless_windowing_checkbox.setObjectName("enable_borderless_windowing_checkbox")
    main_window.terminate_bw_on_exit_checkbox.setObjectName("terminate_bw_on_exit_checkbox")
    main_window.create_overwrite_launcher_checkbox.setObjectName("create_overwrite_launcher_checkbox")
    main_window.create_profile_folders_checkbox.setObjectName("create_profile_folders_checkbox")
    main_window.create_overwrite_joystick_profiles_checkbox.setObjectName("create_overwrite_joystick_profiles_checkbox")
    main_window.launch_sequence_list.setObjectName("launch_sequence_list")
    main_window.exit_sequence_list.setObjectName("exit_sequence_list")
    
    # Add the main layout to the deployment tab layout
    main_window.deployment_tab_layout.addLayout(main_layout)
    
    # Print debug info
    print("Deployment tab populated successfully")

def reset_launch_sequence(main_window):
    """Reset the launch sequence to default order"""
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
    # Save the configuration after resetting
    from Python.ui.config_manager import save_configuration
    save_configuration(main_window)

def reset_exit_sequence(main_window):
    """Reset the exit sequence to default order"""
    main_window.exit_sequence_list.clear()
    main_window.exit_sequence_list.addItems([
        "Post1", 
        "Post2", 
        "Post3", 
        "Monitor-Config", 
        "Taskbar",
        "Controller-Mapper"
    ])
    # Save the configuration after resetting
    from Python.ui.config_manager import save_configuration
    save_configuration(main_window)

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
    """Create a row widget with CEN/LC radio buttons and a path label"""
    row_widget = QWidget()
    row_layout = QHBoxLayout(row_widget)
    row_layout.setContentsMargins(0, 0, 0, 0)

    # Create radio button group
    radio_group = QButtonGroup(row_widget)
    
    # Replace checkboxes with radio buttons
    uoc_radio = QRadioButton("CEN")
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
