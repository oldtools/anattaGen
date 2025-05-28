import configparser
import os
from PyQt6.QtWidgets import QFileDialog, QComboBox, QCheckBox, QLineEdit

def to_snake_case(name):
    """Convert a string to snake_case format"""
    import re
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s-]+(?=[\w])', '_', name.strip()).lower()
    name = re.sub(r'\W', '', name)
    return name

def parse_ini_file(file_path: str) -> configparser.ConfigParser | None:
    """Parse an INI configuration file and return the parsed config"""
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve key case
    try:
        if not config.read(file_path, encoding='utf-8'):
            print(f"Error: Could not read or parse {file_path} in parse_ini_file")
            return None
        print(f"Successfully parsed {file_path}. Sections: {config.sections()}")
        return config
    except Exception as e:
        print(f"Exception during parsing {file_path}: {e}")
        return None

def gather_current_configuration(main_window) -> configparser.ConfigParser:
    """Gather current UI configuration into a ConfigParser object"""
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve case for keys
    
    # Initialize sections
    config["Current Settings"] = {}
    config["Element Locations"] = {}
    config["App Locations"] = {}
    
    # Get the app's root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_root_dir = os.path.dirname(os.path.dirname(script_dir))
    
    # Set app_directory
    config["Current Settings"]["app_directory"] = app_root_dir

    # --- Setup Tab --- 
    source_dirs = [main_window.source_dirs_combo.itemText(i) for i in range(main_window.source_dirs_combo.count())]
    config["Current Settings"]["source_directories"] = "|".join(source_dirs)
    exclude_items = [main_window.exclude_items_combo.itemText(i) for i in range(main_window.exclude_items_combo.count())]
    config["Current Settings"]["exclude_items"] = "|".join(exclude_items)
    config["Current Settings"]["game_managers_present"] = main_window.other_managers_combo.currentText()
    config["Current Settings"]["exclude_selected_manager_games"] = str(main_window.exclude_manager_checkbox.isChecked())
    config["Current Settings"]["logging_verbosity"] = main_window.logging_verbosity_combo.currentText()

    config["Element Locations"]["profiles_directory"] = main_window.profiles_dir_edit.text()
    config["Element Locations"]["launchers_directory"] = main_window.launchers_dir_edit.text()
    config["Element Locations"]["player_1_profile_file"] = main_window.p1_profile_edit.text()
    config["Element Locations"]["player_2_profile_file"] = main_window.p2_profile_edit.text()
    config["Element Locations"]["mediacenter_desktop_profile_file"] = main_window.mediacenter_profile_edit.text()
    config["Element Locations"]["multimonitor_gaming_config_file"] = main_window.multimonitor_gaming_config_edit.text()
    config["Element Locations"]["multimonitor_media_desktop_config_file"] = main_window.multimonitor_media_config_edit.text()
    
    # Convert to string explicitly
    config["Element Locations"]["steam_json_path"] = str(getattr(main_window, 'steam_json_file_path', ''))
    config["Element Locations"]["filtered_steam_cache_path"] = str(getattr(main_window, 'filtered_steam_cache_file_path', ''))

    config["App Locations"]["controller_mapper_app"] = main_window.controller_mapper_app_line_edit.text()
    config["App Locations"]["borderless_windowing_app"] = main_window.borderless_app_line_edit.text()
    config["App Locations"]["multi_monitor_app"] = main_window.multimonitor_app_line_edit.text()
    for i, le in enumerate(main_window.pre_launch_app_line_edits):
        config["App Locations"][f"pre_launch_app_{i+1}"] = le.text()
    for i, le in enumerate(main_window.post_launch_app_line_edits):
        config["App Locations"][f"post_launch_app_{i+1}"] = le.text()
    config["App Locations"]["just_after_launch_app"] = main_window.after_launch_app_line_edit.text()
    config["App Locations"]["just_before_exit_app"] = main_window.before_exit_app_line_edit.text()
    
    if hasattr(main_window, 'after_launch_run_wait_checkbox'):
        config["App Locations"]["just_after_launch_app_run_wait"] = str(main_window.after_launch_run_wait_checkbox.isChecked())
    if hasattr(main_window, 'before_exit_run_wait_checkbox'):
        config["App Locations"]["just_before_exit_app_run_wait"] = str(main_window.before_exit_run_wait_checkbox.isChecked())
    if hasattr(main_window, 'pre_launch_run_wait_checkboxes'):
        for i, cb in enumerate(main_window.pre_launch_run_wait_checkboxes):
            config["App Locations"][f"pre_launch_app_{i+1}_run_wait"] = str(cb.isChecked())
    if hasattr(main_window, 'post_launch_run_wait_checkboxes'):
        for i, cb in enumerate(main_window.post_launch_run_wait_checkboxes):
            config["App Locations"][f"post_launch_app_{i+1}_run_wait"] = str(cb.isChecked())

    config["Current Settings"]["deployment_net_check"] = str(main_window.net_check_checkbox.isChecked())
    config["Current Settings"]["deployment_name_check"] = str(main_window.name_check_checkbox.isChecked())
    config["Current Settings"]["deployment_create_profile_folders"] = str(main_window.create_profile_folders_checkbox.isChecked())
    config["Current Settings"]["deployment_use_kill_list"] = str(main_window.use_kill_list_checkbox.isChecked())
    config["Current Settings"]["deployment_run_as_admin"] = str(main_window.run_as_admin_checkbox.isChecked())
    config["Current Settings"]["deployment_hide_taskbar"] = str(main_window.hide_taskbar_checkbox.isChecked())
    config["Current Settings"]["deployment_enable_launcher"] = str(main_window.enable_launcher_checkbox.isChecked())
    config["Current Settings"]["deployment_apply_mapper_profiles"] = str(main_window.apply_mapper_profiles_checkbox.isChecked())
    config["Current Settings"]["deployment_enable_borderless_windowing"] = str(main_window.enable_borderless_windowing_checkbox.isChecked())
    config["Current Settings"]["deployment_terminate_borderless_on_exit"] = str(main_window.terminate_bw_on_exit_checkbox.isChecked())

    return config

def save_configuration(main_window, config_file=None):
    """Save the current configuration to config.ini"""
    # Get the app's root directory if config_file is not specified
    if config_file is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(os.path.dirname(script_dir))
        config_file = os.path.join(app_root_dir, "config.ini")
    
    config = gather_current_configuration(main_window)
    
    # Write to file
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)
    
    print(f"Configuration saved to {config_file}")

def show_save_configuration_dialog(main_window):
    """Show a file dialog to save configuration"""
    file_path, _ = QFileDialog.getSaveFileName(main_window, "Save Configuration File", "config.ini", "INI Files (*.ini);;All Files (*)")
    if file_path:
        if not file_path.lower().endswith('.ini'):
            file_path += '.ini'
        save_configuration(main_window, file_path)

def apply_loaded_configuration(main_window, config: configparser.ConfigParser):
    """Apply a loaded configuration to the UI"""
    def get_bool(section, key, default=False):
        try: return config.getboolean(section, key)
        except (configparser.NoOptionError, configparser.NoSectionError, ValueError): return default
    def get_str(section, key, default=''):
        try: return config.get(section, key)
        except (configparser.NoOptionError, configparser.NoSectionError): return default
    def set_combo_items(combo_widget: QComboBox, value_str: str):
        combo_widget.clear()
        if value_str:
            combo_widget.addItems(value_str.split('|'))

    if "Current Settings" in config:
        cs = config["Current Settings"]
        set_combo_items(main_window.source_dirs_combo, cs.get("source_directories", ''))
        set_combo_items(main_window.exclude_items_combo, cs.get("exclude_items", ''))
        main_window.other_managers_combo.setCurrentText(cs.get("game_managers_present", "(None)"))
        main_window.exclude_manager_checkbox.setChecked(get_bool("Current Settings","exclude_selected_manager_games"))
        main_window.logging_verbosity_combo.setCurrentText(cs.get("logging_verbosity", "Info"))
        if hasattr(main_window, 'net_check_checkbox'): main_window.net_check_checkbox.setChecked(get_bool("Current Settings","deployment_net_check"))
        if hasattr(main_window, 'name_check_checkbox'): main_window.name_check_checkbox.setChecked(get_bool("Current Settings","deployment_name_check"))
        if hasattr(main_window, 'create_profile_folders_checkbox'): main_window.create_profile_folders_checkbox.setChecked(get_bool("Current Settings","deployment_create_profile_folders"))
        if hasattr(main_window, 'use_kill_list_checkbox'): main_window.use_kill_list_checkbox.setChecked(get_bool("Current Settings","deployment_use_kill_list"))
        if hasattr(main_window, 'run_as_admin_checkbox'): main_window.run_as_admin_checkbox.setChecked(get_bool("Current Settings","deployment_run_as_admin"))
        if hasattr(main_window, 'hide_taskbar_checkbox'): main_window.hide_taskbar_checkbox.setChecked(get_bool("Current Settings","deployment_hide_taskbar"))
        if hasattr(main_window, 'enable_launcher_checkbox'): main_window.enable_launcher_checkbox.setChecked(get_bool("Current Settings","deployment_enable_launcher"))
        if hasattr(main_window, 'apply_mapper_profiles_checkbox'): main_window.apply_mapper_profiles_checkbox.setChecked(get_bool("Current Settings","deployment_apply_mapper_profiles"))
        if hasattr(main_window, 'enable_borderless_windowing_checkbox'): main_window.enable_borderless_windowing_checkbox.setChecked(get_bool("Current Settings","deployment_enable_borderless_windowing"))
        if hasattr(main_window, 'terminate_bw_on_exit_checkbox'): main_window.terminate_bw_on_exit_checkbox.setChecked(get_bool("Current Settings","deployment_terminate_borderless_on_exit"))

    if "Element Locations" in config:
        el = config["Element Locations"]
        if hasattr(main_window, 'profiles_dir_edit'): main_window.profiles_dir_edit.setText(el.get("profiles_directory", ''))
        if hasattr(main_window, 'launchers_dir_edit'): main_window.launchers_dir_edit.setText(el.get("launchers_directory", ''))
        if hasattr(main_window, 'p1_profile_edit'): main_window.p1_profile_edit.setText(el.get("player_1_profile_file", ''))
        if hasattr(main_window, 'p2_profile_edit'): main_window.p2_profile_edit.setText(el.get("player_2_profile_file", ''))
        if hasattr(main_window, 'mediacenter_profile_edit'): main_window.mediacenter_profile_edit.setText(el.get("mediacenter_desktop_profile_file", ''))
        if hasattr(main_window, 'multimonitor_gaming_config_edit'): main_window.multimonitor_gaming_config_edit.setText(el.get("multimonitor_gaming_config_file", ''))
        if hasattr(main_window, 'multimonitor_media_config_edit'): main_window.multimonitor_media_config_edit.setText(el.get("multimonitor_media_desktop_config_file", ''))
        main_window.steam_json_file_path = el.get("steam_json_path", '')
        main_window.filtered_steam_cache_file_path = el.get("filtered_steam_cache_path", '')

    if "App Locations" in config:
        al = config["App Locations"]
        if hasattr(main_window, 'controller_mapper_app_line_edit'): main_window.controller_mapper_app_line_edit.setText(al.get("controller_mapper_app", ''))
        if hasattr(main_window, 'borderless_app_line_edit'): main_window.borderless_app_line_edit.setText(al.get("borderless_windowing_app", ''))
        if hasattr(main_window, 'multimonitor_app_line_edit'): main_window.multimonitor_app_line_edit.setText(al.get("multi_monitor_app", ''))
        if hasattr(main_window, 'pre_launch_app_line_edits'):
            for i, le in enumerate(main_window.pre_launch_app_line_edits):
                le.setText(al.get(f"pre_launch_app_{i+1}", ''))
        if hasattr(main_window, 'post_launch_app_line_edits'):
            for i, le in enumerate(main_window.post_launch_app_line_edits):
                le.setText(al.get(f"post_launch_app_{i+1}", ''))
        if hasattr(main_window, 'after_launch_app_line_edit'): main_window.after_launch_app_line_edit.setText(al.get("just_after_launch_app", ''))
        if hasattr(main_window, 'before_exit_app_line_edit'): main_window.before_exit_app_line_edit.setText(al.get("just_before_exit_app", ''))
        
        if hasattr(main_window, 'after_launch_run_wait_checkbox'):
            main_window.after_launch_run_wait_checkbox.setChecked(get_bool("App Locations", "just_after_launch_app_run_wait"))
        if hasattr(main_window, 'before_exit_run_wait_checkbox'):
            main_window.before_exit_run_wait_checkbox.setChecked(get_bool("App Locations", "just_before_exit_app_run_wait"))
        if hasattr(main_window, 'pre_launch_run_wait_checkboxes'):
            for i, cb in enumerate(main_window.pre_launch_run_wait_checkboxes):
                cb.setChecked(get_bool("App Locations", f"pre_launch_app_{i+1}_run_wait"))
        if hasattr(main_window, 'post_launch_run_wait_checkboxes'):
            for i, cb in enumerate(main_window.post_launch_run_wait_checkboxes):
                cb.setChecked(get_bool("App Locations", f"post_launch_app_{i+1}_run_wait"))

def load_configuration(main_window, config_file=None):
    """Load configuration from config.ini"""
    # Get the app's root directory if config_file is not specified
    if config_file is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root_dir = os.path.dirname(os.path.dirname(script_dir))
        config_file = os.path.join(app_root_dir, "config.ini")
    
    if not os.path.exists(config_file):
        print(f"Configuration file not found: {config_file}")
        return
    
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    # Check if repos.ini exists, if not initialize it
    repos_ini_path = os.path.join(os.path.dirname(config_file), "repos.ini")
    if not os.path.exists(repos_ini_path):
        print("repos.ini not found, initializing from repos.set")
        initialize_repos_config(config_file)
    
    apply_loaded_configuration(main_window, config)
    print(f"Configuration loaded from {config_file}")

def show_import_configuration_dialog(main_window):
    """Show a file dialog to load configuration"""
    file_path, _ = QFileDialog.getOpenFileName(main_window, "Open Configuration File", "", "INI Files (*.ini);;All Files (*)")
    if file_path:
        load_configuration(main_window, file_path)

def connect_dynamic_config_saving(main_window):
    """Connect UI elements to save configuration dynamically when changed"""
    config_file = "config.ini"
    print(f"Connecting dynamic config saving to {config_file}")
    
    # Connect checkboxes
    checkboxes = [
        main_window.net_check_checkbox,
        main_window.name_check_checkbox,
        main_window.create_profile_folders_checkbox,
        main_window.use_kill_list_checkbox,
        main_window.run_as_admin_checkbox,
        main_window.hide_taskbar_checkbox,
        main_window.enable_launcher_checkbox,
        main_window.apply_mapper_profiles_checkbox,
        main_window.enable_borderless_windowing_checkbox,
        main_window.terminate_bw_on_exit_checkbox,
        main_window.exclude_manager_checkbox
    ]
    
    for checkbox in checkboxes:
        checkbox.toggled.connect(lambda checked, mw=main_window, cf=config_file: save_configuration(mw, cf))
    
    # Connect line edits
    line_edits = [
        main_window.profiles_dir_edit,
        main_window.launchers_dir_edit,
        main_window.p1_profile_edit,
        main_window.p2_profile_edit,
        main_window.mediacenter_profile_edit,
        main_window.multimonitor_gaming_config_edit,
        main_window.multimonitor_media_config_edit,
        main_window.controller_mapper_app_line_edit,
        main_window.borderless_app_line_edit,
        main_window.multimonitor_app_line_edit,
        main_window.after_launch_app_line_edit,
        main_window.before_exit_app_line_edit
    ]
    
    for line_edit in line_edits:
        line_edit.textChanged.connect(lambda text, mw=main_window, cf=config_file: save_configuration(mw, cf))
    
    # Connect pre/post launch app line edits
    for le in main_window.pre_launch_app_line_edits:
        le.textChanged.connect(lambda text, mw=main_window, cf=config_file: save_configuration(mw, cf))
    
    for le in main_window.post_launch_app_line_edits:
        le.textChanged.connect(lambda text, mw=main_window, cf=config_file: save_configuration(mw, cf))
    
    # Connect combo boxes
    main_window.source_dirs_combo.currentTextChanged.connect(lambda text, mw=main_window, cf=config_file: save_configuration(mw, cf))
    main_window.exclude_items_combo.currentTextChanged.connect(lambda text, mw=main_window, cf=config_file: save_configuration(mw, cf))
    main_window.other_managers_combo.currentTextChanged.connect(lambda text, mw=main_window, cf=config_file: save_configuration(mw, cf))
    main_window.logging_verbosity_combo.currentTextChanged.connect(lambda text, mw=main_window, cf=config_file: save_configuration(mw, cf))
    
    print("Dynamic config saving connected successfully")

def load_initial_config(main_window):
    """Load the initial configuration from config.ini"""
    # Try to find config.ini in the current directory first
    current_dir_config = "config.ini"
    if os.path.exists(current_dir_config):
        print(f"Loading configuration from {current_dir_config}")
        load_configuration(main_window, current_dir_config)
        connect_dynamic_config_saving(main_window)
        return True
        
    # If not found, try to find it in the parent directory (Python folder)
    parent_dir_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini')
    if os.path.exists(parent_dir_config):
        print(f"Loading configuration from {parent_dir_config}")
        load_configuration(main_window, parent_dir_config)
        connect_dynamic_config_saving(main_window)
        return True
    
    # If still not found, try to find it in the Python/ui directory
    ui_dir_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    if os.path.exists(ui_dir_config):
        print(f"Loading configuration from {ui_dir_config}")
        load_configuration(main_window, ui_dir_config)
        connect_dynamic_config_saving(main_window)
        return True
    
    # If no config.ini found, use default settings
    print("No config.ini found. Using default settings.")
    main_window.statusBar().showMessage("No default configuration found. Using default settings.", 5000)
    connect_dynamic_config_saving(main_window)
    return False

def initialize_repos_config(config_file=None):
    """Initialize repos.ini based on Python\repos.set and app_directory from config.ini"""
    # Get the app's root directory if config_file is not specified
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_root_dir = os.path.dirname(os.path.dirname(script_dir))
    
    if config_file is None:
        config_file = os.path.join(app_root_dir, "config.ini")
    
    # Load the main config to get app_directory
    main_config = configparser.ConfigParser()
    main_config.read(config_file, encoding='utf-8')
    
    app_directory = main_config.get("Current Settings", "app_directory", fallback=app_root_dir)
    
    # Load repos.set
    repos_set_path = os.path.join(app_directory, "Python", "repos.set")
    if not os.path.exists(repos_set_path):
        print(f"repos.set not found at {repos_set_path}")
        return False
    
    repos_config = configparser.ConfigParser()
    
    # Try different encodings
    encodings = ['utf-8-sig', 'utf-16', 'latin-1', 'cp1252']
    success = False
    
    for encoding in encodings:
        try:
            print(f"Trying to read repos.set with {encoding} encoding")
            repos_config.read(repos_set_path, encoding=encoding)
            success = True
            print(f"Successfully read repos.set with {encoding} encoding")
            break
        except UnicodeDecodeError:
            print(f"Failed to read repos.set with {encoding} encoding")
            continue
    
    if not success:
        print("Failed to read repos.set with any encoding")
        return False
    
    # Get SOURCEHOST from GLOBAL section
    source_host = repos_config.get("GLOBAL", "SOURCEHOST", fallback="")
    
    # Create repos.ini
    repos_ini_path = os.path.join(app_directory, "repos.ini")
    repos_ini = configparser.ConfigParser()
    
    # Copy sections from repos.set to repos.ini
    for section in repos_config.sections():
        if section != "GLOBAL":  # Skip the GLOBAL section
            repos_ini[section] = {}
            for key, value in repos_config[section].items():
                # Replace $ITEMNAME with the section name
                value = value.replace("$ITEMNAME", section)
                # Replace $EXTRACTLOC with app_directory
                value = value.replace("$EXTRACTLOC", app_directory)
                # Replace $SOURCEHOST with the value from GLOBAL section
                value = value.replace("$SOURCEHOST", source_host)
                repos_ini[section][key] = value
    
    # Write to repos.ini
    with open(repos_ini_path, 'w', encoding='utf-8') as f:
        repos_ini.write(f)
    
    print(f"Initialized repos.ini at {repos_ini_path}")
    return True
