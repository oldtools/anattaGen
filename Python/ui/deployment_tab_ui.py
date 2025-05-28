# Python/ui/deployment_tab_ui.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QHBoxLayout, QFormLayout, QCheckBox
)
# Assuming ui_widgets.py is in the same directory (Python.ui)
from .ui_widgets import create_deployment_path_row_widget

def populate_deployment_tab(main_window: QWidget, tab_widget):
    """Populate the Deployment tab with UI elements"""
    # Use the existing deployment_tab instead of creating a new one
    deployment_tab = main_window.deployment_tab
    main_layout = QVBoxLayout(deployment_tab)
    
    # --- Instantiate all checkboxes first to ensure they exist for layout ---
    # These become attributes of main_window
    main_window.net_check_checkbox = QCheckBox("Net-Check (Verify internet connection before launch)")
    main_window.enable_borderless_windowing_checkbox = QCheckBox("Enable Borderless Windowing App (if defined in Setup)")
    main_window.terminate_bw_on_exit_checkbox = QCheckBox("Terminate Borderless Windowing App on Game Exit")
    main_window.name_check_checkbox = QCheckBox("Name-Check (Lookup titles in Steam Cache for IDs)")
    main_window.create_profile_folders_checkbox = QCheckBox("Profile Folders (Create if non-existent)")
    main_window.use_kill_list_checkbox = QCheckBox("Enable Kill-List (Terminate specified processes pre-launch)")
    main_window.run_as_admin_checkbox = QCheckBox("Launch Games As Administrator")
    main_window.hide_taskbar_checkbox = QCheckBox("Attempt to Hide Taskbar During Gameplay")
    main_window.enable_launcher_checkbox = QCheckBox("Use Game-Specific Launcher (if defined in Setup)")
    main_window.apply_mapper_profiles_checkbox = QCheckBox("Create / Overwrite Joystick Mapping Profiles  (even if not defined)")

    # --- Connect dependent checkboxes ---
    main_window.terminate_bw_on_exit_checkbox.setEnabled(main_window.enable_borderless_windowing_checkbox.isChecked())
    main_window.enable_borderless_windowing_checkbox.toggled.connect(main_window.terminate_bw_on_exit_checkbox.setEnabled)

    # --- Top section for Update Steam Cache and Process Steam Cache buttons ---
    top_buttons_layout = QHBoxLayout()
    main_window.update_steam_json_button = QPushButton("Update Steam Cache (steam.json)")
    main_window.update_steam_json_button.clicked.connect(main_window._update_steam_json_cache) # Connects to MainWindow method
    
    main_window.process_steam_json_button = QPushButton("Process Steam Cache File")
    main_window.process_steam_json_button.clicked.connect(main_window._prompt_and_process_steam_json)
    
    top_buttons_layout.addStretch(1)
    top_buttons_layout.addWidget(main_window.update_steam_json_button)
    top_buttons_layout.addWidget(main_window.process_steam_json_button)
    main_layout.addLayout(top_buttons_layout)
    
    # --- Two-column layout for general options checkboxes ---
    general_options_group_box = QWidget() 
    general_options_columns_layout = QHBoxLayout(general_options_group_box)
    
    column1_layout = QVBoxLayout()
    column1_layout.addWidget(main_window.enable_borderless_windowing_checkbox)
    bw_terminate_sub_layout = QHBoxLayout()
    bw_terminate_sub_layout.addSpacing(20) 
    bw_terminate_sub_layout.addWidget(main_window.terminate_bw_on_exit_checkbox)
    bw_terminate_sub_layout.addStretch()
    column1_layout.addLayout(bw_terminate_sub_layout)
    column1_layout.addWidget(main_window.create_profile_folders_checkbox)
    column1_layout.addWidget(main_window.enable_launcher_checkbox)
    column1_layout.addWidget(main_window.apply_mapper_profiles_checkbox)
    column1_layout.addWidget(main_window.run_as_admin_checkbox)
    column1_layout.addWidget(main_window.hide_taskbar_checkbox)
    column1_layout.addStretch(1)

    column2_layout = QVBoxLayout()
    column2_layout.addWidget(main_window.net_check_checkbox)
    column2_layout.addWidget(main_window.name_check_checkbox)
    column2_layout.addWidget(main_window.use_kill_list_checkbox)
    column2_layout.addStretch(1)

    general_options_columns_layout.addLayout(column1_layout)
    general_options_columns_layout.addLayout(column2_layout)
    
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
        ("Just After Launch App:", main_window.after_launch_app_line_edit if hasattr(main_window, 'after_launch_app_line_edit') else None),
        ("Just Before Exit App:", main_window.before_exit_app_line_edit if hasattr(main_window, 'before_exit_app_line_edit') else None),
    ]
    for i in range(3):
        if hasattr(main_window, 'pre_launch_app_line_edits') and i < len(main_window.pre_launch_app_line_edits):
            paths_to_display.append((f"Pre-Launch App {i+1}:", main_window.pre_launch_app_line_edits[i]))
        else:
            paths_to_display.append((f"Pre-Launch App {i+1}:", None))
    for i in range(3):
        if hasattr(main_window, 'post_launch_app_line_edits') and i < len(main_window.post_launch_app_line_edits):
            paths_to_display.append((f"Post-Launch App {i+1}:", main_window.post_launch_app_line_edits[i]))
        else:
            paths_to_display.append((f"Post-Launch App {i+1}:", None))
            
    for label_text, setup_qlineedit in paths_to_display:
        if setup_qlineedit:
            # Use the imported function create_deployment_path_row_widget
            # It expects parent_window (main_window) and the QLineEdit to mirror
            path_row_container_widget, _, _, _ = create_deployment_path_row_widget(main_window, setup_qlineedit)
            middle_section_form_layout.addRow(label_text, path_row_container_widget)
        else:
             middle_section_form_layout.addRow(label_text, QLabel("<i>Path not configured in Setup Tab</i>"))
    main_layout.addLayout(middle_section_form_layout)
    
    # --- Bottom Section for Index buttons ---
    bottom_button_layout = QHBoxLayout()
    main_window.index_sources_button = QPushButton("Index Sources")
    main_window.index_sources_button.clicked.connect(main_window._index_sources) # Connects to MainWindow method
    # Load Index button removed
    bottom_button_layout.addStretch(1)
    bottom_button_layout.addWidget(main_window.index_sources_button)
    # Load Index button removed
    bottom_button_layout.addStretch(1)
    main_layout.addLayout(bottom_button_layout)
    main_layout.addStretch(1) 
    
    # Remove this line - we don't need to add the tab again
    # tab_widget.addTab(deployment_tab, "Deployment")
