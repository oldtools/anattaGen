import os 
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QLineEdit, QHBoxLayout, QFormLayout, QFileDialog, QCheckBox
)
from .ui_widgets import (
    create_path_selection_widget,
    create_app_selection_with_flyout_widget,
    create_app_selection_with_run_wait_widget,
    create_list_management_widget
)

def populate_setup_tab(main_window: QWidget): 
    main_layout = QVBoxLayout(main_window.setup_tab) 

    config_button_layout = QHBoxLayout()
    main_window.import_config_button = QPushButton("Import Configuration File")
    main_window.import_config_button.clicked.connect(main_window._import_configuration_dialog)
    main_window.save_config_button = QPushButton("Save Configuration File")
    main_window.save_config_button.clicked.connect(main_window._show_save_configuration_dialog)
    main_window.process_steam_json_button = QPushButton("Process Steam Cache File")
    main_window.process_steam_json_button.clicked.connect(main_window._prompt_and_process_steam_json)
    
    config_button_layout.addWidget(main_window.import_config_button)
    config_button_layout.addWidget(main_window.save_config_button)
    config_button_layout.addWidget(main_window.process_steam_json_button)
    config_button_layout.addStretch(1)
    main_layout.addLayout(config_button_layout)

    form_layout = QFormLayout()
    form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)

    main_window.source_dirs_widget, main_window.source_dirs_combo = create_list_management_widget(main_window, is_directory_list=True)
    form_layout.addRow(QLabel("Source Game Dirs:"), main_window.source_dirs_widget)

    main_window.exclude_items_widget, main_window.exclude_items_combo = create_list_management_widget(main_window, is_directory_list=False) 
    form_layout.addRow(QLabel("Exclude Items (Dirs/Patterns):"), main_window.exclude_items_widget)

    main_window.other_managers_combo = QComboBox()
    main_window.other_managers_combo.addItems(["(None)", "Steam", "Epic Games", "Amazon Games", "Microsoft Store/Xbox", "GOG Galaxy", "Other"])
    main_window.exclude_manager_checkbox = QCheckBox("Exclude Games")
    main_window.locate_manager_config_button = QPushButton("Locate & Exclude Config")
    main_window.locate_manager_config_button.clicked.connect(main_window._locate_and_exclude_manager_config) 
    
    manager_options_layout = QHBoxLayout()
    manager_options_layout.addWidget(main_window.other_managers_combo, 1)
    manager_options_layout.addWidget(main_window.exclude_manager_checkbox)
    manager_options_layout.addWidget(main_window.locate_manager_config_button)
    manager_options_widget = QWidget()
    manager_options_widget.setLayout(manager_options_layout)
    form_layout.addRow(QLabel("Game Managers Present:"), manager_options_widget)

    # The _add_new_app_dialog method is still in MainWindow, so lambdas call main_window._add_new_app_dialog
    # The create_app_selection_with_flyout_widget handles connecting its internal "Add New..." action
    # to call parent_window._add_new_app_dialog with its internally created QLineEdit.
    main_window.predefined_controller_apps = {
        "AntimicroX": "Path/To/AntimicroX.exe", "Keysticks": "Path/To/Keysticks.exe",
        "DS4Windows": "Path/To/DS4Windows.exe", "JoyXoff": "Path/To/JoyXoff.exe",
        "SteamInput": "Configure within Steam", 
        "Add New...": main_window._add_new_app_dialog # Pass the method directly; helper will provide the QLineEdit
    }
    main_window.predefined_borderless_apps = {
        "Magpie": "Path/To/Magpie.exe", "Borderless Gaming": "Path/To/BorderlessGaming.exe",
        "Special K": "Path/To/SpecialK.exe",
        "Add New...": main_window._add_new_app_dialog
    }
    main_window.predefined_multimonitor_apps = {
        "MultiMonitorTool": "Path/To/MultiMonitorTool.exe", "Display-Changer": "Path/To/Display-Changer.exe",
        "Script": "Path/To/YourMultiMonitorScript.bat", 
        "Add New...": main_window._add_new_app_dialog
    }

    widget, main_window.profiles_dir_edit = create_path_selection_widget(main_window, "Select Profiles Directory", is_directory=True)
    form_layout.addRow(QLabel("Profiles Directory:"), widget)
    widget, main_window.launchers_dir_edit = create_path_selection_widget(main_window, "Select Launchers Directory", is_directory=True)
    form_layout.addRow(QLabel("Launchers Directory:"), widget)

    widget, main_window.controller_mapper_app_line_edit = create_app_selection_with_flyout_widget(
        main_window, "Select Controller Mapper Application", main_window.predefined_controller_apps
    )
    form_layout.addRow(QLabel("Controller Mapper App:"), widget)

    widget, main_window.borderless_app_line_edit = create_app_selection_with_flyout_widget(
        main_window, "Select Borderless Windowing Application", main_window.predefined_borderless_apps
    )
    form_layout.addRow(QLabel("Borderless Windowing App:"), widget)

    widget, main_window.multimonitor_app_line_edit = create_app_selection_with_flyout_widget(
        main_window, "Select Multi-Monitor Application", main_window.predefined_multimonitor_apps
    )
    form_layout.addRow(QLabel("Multi-Monitor App:"), widget)

    widget, main_window.p1_profile_edit = create_path_selection_widget(main_window, "Select Player 1 Profile File", is_directory=False)
    form_layout.addRow(QLabel("Player 1 Profile File:"), widget)
    widget, main_window.p2_profile_edit = create_path_selection_widget(main_window, "Select Player 2 Profile File", is_directory=False)
    form_layout.addRow(QLabel("Player 2 Profile File:"), widget)
    widget, main_window.mediacenter_profile_edit = create_path_selection_widget(main_window, "Select Media Center/Desktop Profile File", is_directory=False)
    form_layout.addRow(QLabel("Media Center/Desktop Profile File:"), widget)
    widget, main_window.multimonitor_gaming_config_edit = create_path_selection_widget(main_window, "Select Multi-Monitor Gaming Config File", is_directory=False)
    form_layout.addRow(QLabel("MM Gaming Config File:"), widget)
    widget, main_window.multimonitor_media_config_edit = create_path_selection_widget(main_window, "Select Multi-Monitor Media/Desktop Config File", is_directory=False)
    form_layout.addRow(QLabel("MM Media/Desktop Config File:"), widget)
    
    main_window.pre_launch_app_line_edits = []
    main_window.pre_launch_run_wait_checkboxes = []
    main_window.post_launch_app_line_edits = []
    main_window.post_launch_run_wait_checkboxes = []

    # For apps with Run-Wait, the predefined_apps dict passed to the helper
    # should also use the main_window._add_new_app_dialog for its "Add New..." action.
    # The helper (create_app_selection_with_run_wait_widget -> create_app_selection_with_flyout_widget)
    # will handle connecting this to its internal QLineEdit.
    predefined_run_wait_apps_template = {
        "Add New...": main_window._add_new_app_dialog
    }

    for i in range(1, 4):
        widget, line_edit, run_wait_cb = create_app_selection_with_run_wait_widget(
            main_window, f"Select Pre-Launch App {i}", predefined_run_wait_apps_template
        )
        main_window.pre_launch_app_line_edits.append(line_edit)
        main_window.pre_launch_run_wait_checkboxes.append(run_wait_cb)
        form_layout.addRow(QLabel(f"Pre-Launch App {i}:"), widget)

    for i in range(1, 4):
        widget, line_edit, run_wait_cb = create_app_selection_with_run_wait_widget(
            main_window, f"Select Post-Launch App {i}", predefined_run_wait_apps_template
        )
        main_window.post_launch_app_line_edits.append(line_edit)
        main_window.post_launch_run_wait_checkboxes.append(run_wait_cb)
        form_layout.addRow(QLabel(f"Post-Launch App {i}:"), widget)

    widget, main_window.after_launch_app_line_edit, main_window.after_launch_run_wait_checkbox = \
        create_app_selection_with_run_wait_widget(
            main_window, "Select After Launch App", predefined_run_wait_apps_template
        )
    form_layout.addRow(QLabel("Just After Launch App:"), widget)

    widget, main_window.before_exit_app_line_edit, main_window.before_exit_run_wait_checkbox = \
        create_app_selection_with_run_wait_widget(
            main_window, "Select Before Exit App", predefined_run_wait_apps_template
        )
    form_layout.addRow(QLabel("Just Before Exit App:"), widget)
    
    main_window.logging_verbosity_combo = QComboBox()
    main_window.logging_verbosity_combo.addItems(["None", "Error", "Warning", "Info", "Debug", "Trace"])
    main_window.logging_verbosity_combo.setCurrentText("Info")
    form_layout.addRow(QLabel("Logging Verbosity:"), main_window.logging_verbosity_combo)
    
    main_layout.addLayout(form_layout)
    main_layout.addStretch(1) 