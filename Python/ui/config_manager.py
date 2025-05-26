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

    config["Current Settings"] = {}
    config["Element Locations"] = {}
    config["App Locations"] = {}

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
    config["Element Locations"]["steam_json_path"] = getattr(main_window, 'steam_json_file_path', '')
    config["Element Locations"]["filtered_steam_cache_path"] = getattr(main_window, 'filtered_steam_cache_file_path', '')

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

def save_configuration(main_window, file_path: str):
    """Save the current configuration to the specified file"""
    config = gather_current_configuration(main_window)
    try:
        with open(file_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        main_window.statusBar().showMessage(f"Configuration saved to {file_path}", 5000)
    except Exception as e:
        main_window.statusBar().showMessage(f"Error saving configuration: {e}", 5000)
        print(f"Error saving configuration: {e}")

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

def load_configuration(main_window, file_path: str):
    """Load configuration from a file and apply it to the UI"""
    loaded_config = parse_ini_file(file_path)
    if loaded_config:
        apply_loaded_configuration(main_window, loaded_config)
        main_window.statusBar().showMessage(f"Configuration loaded from {file_path}", 5000)
        return True
    else:
        main_window.statusBar().showMessage(f"Failed to load or parse {file_path}", 5000)
        return False

def show_import_configuration_dialog(main_window):
    """Show a file dialog to load configuration"""
    file_path, _ = QFileDialog.getOpenFileName(main_window, "Open Configuration File", "", "INI Files (*.ini);;All Files (*)")
    if file_path:
        load_configuration(main_window, file_path)

def load_initial_config(main_window):
    default_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.ini')
    if os.path.exists(default_config_path):
        load_configuration(main_window, default_config_path)
    else:
        main_window.statusBar().showMessage("No default configuration found. Using default settings.", 5000) 