"""
Main Application for the Assetto Corsa Server Configuration Manager

This module provides the main GUI window that orchestrates configuration management
for Assetto Corsa servers with support for the Virtual Steward replay plugin.

Architecture:
- ACServerConfigGUI: Main window that coordinates tab components and config state
- Tab Components: Each configuration area is a separate tab (server config, VS plugin, advanced options)
- Config State: Entry list data is maintained in memory and written to disk on save
- Virtual Steward Integration: Automatic skin modification for bot entries when VS is enabled

Key Responsibilities:
1. Config File I/O: Load/save INI (server_cfg.ini, entry_list.ini) and YAML files
2. UI State Management: Populate fields from configs, track unsaved changes
3. Virtual Steward: Manage bot entry modifications (skin suffix, GUID assignment)
4. Cross-tab Communication: Coordinate updates between tab components (e.g., VS enable affects entry list)

Configuration Workflow:
- Load: Reads all configs from server directory into memory (self.configs)
- Display: Populates UI fields from config data
- Edit: User modifies configs through UI
- Save: Validates fields, updates configs, writes to disk, reloads for sync

Virtual Steward Considerations:
- Bot entries are the first N entries in the entry list
- Bots require '/VS' suffix on their car skin
- GUIDs are auto-assigned for bots (8888880 + index) and cleared for players
- When VS is toggled, entry list is automatically updated
"""

import sys
import configparser
import subprocess
from pathlib import Path
from typing import Dict, List

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QMessageBox, QTableWidgetItem
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QBrush
from PyQt5.QtCore import Qt, QSettings

from utils import get_resource_path, format_display_string
import file_manager
import config_manager
from main_menu_tab import MainMenuTab
from server_config_tab import ServerConfigTab
from virtual_steward_tab import VirtualStewardTab
from advanced_options_tab import AdvancedOptionsTab


class ACServerConfigGUI(QMainWindow):
    """Main application window for the Assetto Corsa Server Configuration Manager"""
    
    def __init__(self):
        super().__init__()
        self.content_root = None
        self.server_root = None
        self.servers_parent_dir = None
        self.configs = {}
        
        # Track data
        self.available_tracks = []
        self.track_display_map = {}
        self.available_cars = {}
        self.available_weather = []
        self.entry_list_data = []
        
        # Unsaved changes
        self.has_unsaved_changes = False
        
        # Settings
        self.settings = QSettings('ACServerConfig', 'ACServerConfigManager')
        
        # Tab references
        self.main_menu_tab = None
        self.server_config_tab = None
        self.virtual_steward_tab = None
        self.advanced_options_tab = None
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Virtual Steward Server Manager")
        self.setGeometry(100, 100, 1400, 800)
        
        # Set window icon
        icon_path = Path(__file__).parent / "files" / "Icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # LEFT PANEL: Tabbed Interface
        left_panel = self.create_left_tabbed_panel()
        main_layout.addWidget(left_panel, 1)
        
        main_widget.setLayout(main_layout)
    
    def create_left_tabbed_panel(self) -> QTabWidget:
        """Create the left tabbed panel"""
        tab_widget = QTabWidget()
        
        # Tab 1: Main Menu (with integrated Server Terminal)
        self.main_menu_tab = MainMenuTab(self)
        tab_widget.addTab(self.main_menu_tab, "Main Menu")
        
        # Tab 2: Server Configuration
        self.server_config_tab = ServerConfigTab(self)
        tab_widget.addTab(self.server_config_tab, "Server Configuration")
        
        # Tab 3: Virtual Steward
        self.virtual_steward_tab = VirtualStewardTab(self)
        tab_widget.addTab(self.virtual_steward_tab, "Virtual Steward")
        
        # Tab 4: Advanced Options
        self.advanced_options_tab = AdvancedOptionsTab(self)
        tab_widget.addTab(self.advanced_options_tab, "Advanced Options")

        return tab_widget
    
    def load_settings(self):
        """Load saved settings from previous sessions"""
        ac_root = self.settings.value('ac_content_root', '')
        servers_parent_dir = self.settings.value('servers_parent_dir', '')
        server_root = self.settings.value('server_root', '')
        
        if ac_root and Path(ac_root).exists():
            self.content_root = ac_root
            self.main_menu_tab.ac_root_input.setText(ac_root)
            self.on_content_discovery_changed()

        if servers_parent_dir and Path(servers_parent_dir).exists():
            self.servers_parent_dir = servers_parent_dir
            self.main_menu_tab.server_root_input.setText(servers_parent_dir)
            self.main_menu_tab.populate_servers_list()
            
            if server_root:
                server_cfg_path = Path(server_root) / "cfg" / "server_cfg.ini"
                entry_list_path = Path(server_root) / "cfg" / "entry_list.ini"
                if server_cfg_path.exists() and entry_list_path.exists():
                    self.server_root = server_root
                    self.auto_load_configs()
                    self.main_menu_tab._select_server_in_list(server_root)
                else:
                    self.settings.remove('server_root')
        elif server_root:
            # Legacy: derive parent from server_root
            server_cfg_path = Path(server_root) / "cfg" / "server_cfg.ini"
            entry_list_path = Path(server_root) / "cfg" / "entry_list.ini"
            if server_cfg_path.exists() and entry_list_path.exists():
                parent = str(Path(server_root).parent)
                self.servers_parent_dir = parent
                self.main_menu_tab.server_root_input.setText(parent)
                self.settings.setValue('servers_parent_dir', parent)
                self.main_menu_tab.populate_servers_list()
                self.server_root = server_root
                self.auto_load_configs()
                self.main_menu_tab._select_server_in_list(server_root)
            else:
                self.settings.remove('server_root')
    
    def on_content_discovery_changed(self):
        """Called when content root changes - discover available resources"""
        self.discover_tracks()
        self.discover_cars()
        self.discover_weather()
    
    def discover_tracks(self):
        """Discover available tracks"""
        self.available_tracks, self.track_display_map = file_manager.discover_tracks(self.content_root)
    
    def discover_cars(self):
        """Discover available cars"""
        self.available_cars = file_manager.discover_cars(self.content_root)
    
    def discover_weather(self):
        """Discover available weather"""
        self.available_weather = file_manager.discover_weather(self.content_root)
    
    def save_settings(self):
        """Save settings for next session"""
        if self.content_root:
            self.settings.setValue('ac_content_root', self.content_root)
        if self.servers_parent_dir:
            self.settings.setValue('servers_parent_dir', self.servers_parent_dir)
        if self.server_root:
            self.settings.setValue('server_root', self.server_root)
    
    def auto_load_configs(self):
        """Load all config files from selected server"""
        if not self.server_root:
            return

        try:
            self.configs = config_manager.load_configs(self.server_root)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configurations: {str(e)}")
            self.server_root = None
            self.main_menu_tab.server_root_input.clear()
            self.settings.remove('server_root')
            return

        self.populate_all_fields()
    
    def populate_all_fields(self):
        """
        Populate all widgets in all tabs from loaded configs.
        
        Sequence is important:
        1. Server config first (populates track, ports, etc.)
        2. Entry list (populates player/bot data)
        3. Virtual Steward and extra config
        4. Bot trains config
        5. Advanced options
        6. Refresh display and update dependent controls (VS enable state affects entry list visibility)
        7. Reset unsaved changes flag
        """
        # Server Configuration tab (core server settings)
        if 'server_cfg.ini' in self.configs:
            self.populate_server_config(self.configs['server_cfg.ini']['parser'])

        # Entry list (player and bot entries)
        if 'entry_list.ini' in self.configs:
            self.populate_entry_list(self.configs['entry_list.ini']['parser'])

        # Virtual Steward plugin description
        yaml_config = self.configs.get('extra_cfg.yml', {}).get('data') or {}
        self.populate_server_description(yaml_config)

        # Bot trains configuration (depends on entry list being loaded)
        plugin_config = self.configs.get('plugin_vs_replay_cfg.yml', {}).get('data') or {}
        self.populate_bot_trains_config(plugin_config)

        # Advanced Options (weather, logging, admin settings)
        server_cfg = self.configs['server_cfg.ini']['parser'] if 'server_cfg.ini' in self.configs else configparser.ConfigParser()
        self.populate_advanced_options(server_cfg, yaml_config)

        # Refresh the display and update dependent controls
        self.refresh_entry_list_table()
        self.on_vs_enabled_changed()  # Update VS-dependent control visibility
        
        self.has_unsaved_changes = False
    
    def populate_server_config(self, config: configparser.ConfigParser):
        """Populate server config fields"""
        if 'SERVER' not in config:
            QMessageBox.warning(self, "Warning", "SERVER section not found in server_cfg.ini")
            return
        
        server_section = config['SERVER']
        widgets = self.server_config_tab.server_config_widgets
        
        # NAME
        if 'NAME' in server_section:
            widgets['NAME'].setText(server_section['NAME'])
        
        # TRACK
        if 'TRACK' in server_section:
            current_track = server_section['TRACK']
            widgets['TRACK'].setText(format_display_string(current_track))
            widgets['TRACK'].setProperty('original_track', current_track)
        
        # UDP, TCP, HTTP ports
        if 'UDP_PORT' in server_section:
            widgets['UDP_PORT'].setText(server_section['UDP_PORT'])
        if 'TCP_PORT' in server_section:
            widgets['TCP_PORT'].setText(server_section['TCP_PORT'])
        if 'HTTP_PORT' in server_section:
            widgets['HTTP_PORT'].setText(server_section['HTTP_PORT'])

        # TIME OF DAY
        if 'TIME_OF_DAY_MULT' in server_section:
            val = server_section['TIME_OF_DAY_MULT'].strip()
            widgets['TIME_OF_DAY_MULT'].setChecked(val != '0')

        # SUN_ANGLE to TIME_OF_DAY mapping
        tod_times = [0, 300, 600, 900, 1200, 1500, 1800, 2100]
        if 'SUN_ANGLE' in server_section:
            try:
                sun = float(server_section['SUN_ANGLE'])
                tod_int = round((sun + 135) / 0.15)
                closest = min(tod_times, key=lambda t: abs(t - tod_int))
                idx = tod_times.index(closest)
                widgets['TIME_OF_DAY'].setCurrentIndex(idx)
            except ValueError:
                pass

    def populate_entry_list(self, config: configparser.ConfigParser):
        """Populate entry list from entry_list.ini"""
        self.entry_list_data = []
        
        car_sections = [s for s in config.sections() if s.upper().startswith('CAR_')]
        car_sections.sort(key=lambda x: int(x.split('_')[1]))
        
        for section in car_sections:
            model = config.get(section, 'MODEL', fallback='')
            skin = config.get(section, 'SKIN', fallback='')
            spectator_mode = config.get(section, 'SPECTATOR_MODE', fallback='0')
            drivername = config.get(section, 'DRIVERNAME', fallback='')
            team = config.get(section, 'TEAM', fallback='')
            guid = config.get(section, 'GUID', fallback='')
            ballast = config.get(section, 'BALLAST', fallback='0')
            restrictor = config.get(section, 'RESTRICTOR', fallback='0')
            
            self.entry_list_data.append({
                'section': section,
                'model': model,
                'skin': skin,
                'spectator_mode': spectator_mode,
                'drivername': drivername,
                'team': team,
                'guid': guid,
                'ballast': ballast,
                'restrictor': restrictor
            })
        
        self.update_num_bots_combo_range()
        self.refresh_entry_list_table()
    
    def populate_server_description(self, yaml_config: dict):
        """Populate server description from extra_cfg.yml"""
        widgets = self.server_config_tab.server_config_widgets
        if 'SERVER_DESCRIPTION' in widgets:
            description = yaml_config.get('ServerDescription', '')
            if description:
                widgets['SERVER_DESCRIPTION'].setPlainText(description)
        
        # VS checkbox
        enable_plugins = yaml_config.get('EnablePlugins', [])
        if enable_plugins is None:
            enable_plugins = []
        is_vs_enabled = 'VSReplayPlugin' in enable_plugins
        self.virtual_steward_tab.vs_enabled_checkbox.setChecked(is_vs_enabled)
    
    def populate_bot_trains_config(self, plugin_config: dict):
        """
        Populate bot trains configuration from plugin_vs_replay_cfg.yml
        
        Configuration Key Mappings:
        - AutoStartOffset: Controls both "bot trains enabled" state and train gap
          * If 0: Bot trains are disabled
          * If != 0: Bot trains are enabled, value becomes the gap between bots
          * Valid range: 5-100 (clamped to slider range)
        - LoopLap: Number of laps to loop the replay
        - AutoStart: Number of bots to automatically start (determines num_bots_combo value)
        """
        tab = self.virtual_steward_tab
        
        if hasattr(tab, 'bot_trains_checkbox') and hasattr(tab, 'train_gap_slider'):
            # AutoStartOffset is the key that controls both enabled state and gap value
            auto_start_offset = plugin_config.get('AutoStartOffset', 0)
            is_bot_trains_enabled = auto_start_offset != 0
            tab.bot_trains_checkbox.setChecked(is_bot_trains_enabled)
            
            if isinstance(auto_start_offset, (int, float)):
                # Clamp to valid slider range (5-100)
                slider_value = max(5, min(100, int(auto_start_offset)))
                tab.train_gap_slider.setValue(slider_value)
                tab.train_gap_value_label.setText(str(slider_value))
        
        if hasattr(tab, 'loop_lap_input'):
            loop_lap = plugin_config.get('LoopLap', '')
            tab.loop_lap_input.setText(str(loop_lap) if loop_lap != '' else '')
        
        if hasattr(tab, 'num_bots_combo'):
            # AutoStart specifies how many bots are configured in the plugin
            auto_start = plugin_config.get('AutoStart', 0)
            auto_start = int(auto_start) if isinstance(auto_start, (int, float)) else 0
            self.update_num_bots_combo_range(set_value=auto_start)
    
    def populate_advanced_options(self, server_config: configparser.ConfigParser, yaml_config: dict):
        """Populate Advanced Options tab"""
        tab = self.advanced_options_tab
        
        # Weather
        if hasattr(tab, 'weather_dropdown'):
            tab.weather_dropdown.blockSignals(True)
            tab.weather_dropdown.clear()
            
            for weather in self.available_weather:
                tab.weather_dropdown.addItem(weather)
            
            if 'WEATHER_0' in server_config and 'GRAPHICS' in server_config['WEATHER_0']:
                graphics_value = server_config['WEATHER_0']['GRAPHICS']
                index = tab.weather_dropdown.findText(graphics_value)
                if index >= 0:
                    tab.weather_dropdown.setCurrentIndex(index)
            
            tab.weather_dropdown.blockSignals(False)
        
        # Force Headlights
        if hasattr(tab, 'force_headlights_checkbox'):
            force_lights = yaml_config.get('ForceLights', False)
            tab.force_headlights_checkbox.setChecked(force_lights)
        
        # Tires Allowed Out
        if hasattr(tab, 'tires_allowed_dropdown'):
            if 'SERVER' in server_config and 'ALLOWED_TYRES_OUT' in server_config['SERVER']:
                tires_value = server_config['SERVER']['ALLOWED_TYRES_OUT']
                index = tab.tires_allowed_dropdown.findText(tires_value)
                if index >= 0:
                    tab.tires_allowed_dropdown.setCurrentIndex(index)
        
        # Loading URL
        if hasattr(tab, 'loading_image_url_input'):
            loading_urls = yaml_config.get('LoadingImageUrls', None)
            if loading_urls and isinstance(loading_urls, list) and len(loading_urls) > 0:
                tab.loading_image_url_input.setText(loading_urls[0])
        
        # Client Send Interval HZ
        if hasattr(tab, 'client_send_interval_input'):
            if 'SERVER' in server_config and 'CLIENT_SEND_INTERVAL_HZ' in server_config['SERVER']:
                hz_value = server_config['SERVER']['CLIENT_SEND_INTERVAL_HZ']
                tab.client_send_interval_input.setText(hz_value)
        
        # Player Loading Timeout
        if hasattr(tab, 'player_loading_timeout_input'):
            timeout_value = yaml_config.get('PlayerLoadingTimeoutMinutes', 10)
            tab.player_loading_timeout_input.setText(str(timeout_value))
        
        # Admins
        if hasattr(tab, 'admins_list_widget'):
            tab.admins_list_widget.clear()
            admins_lines = file_manager.read_text_file(str(Path(self.server_root) / 'admins.txt'))
            for line in admins_lines:
                tab.admins_list_widget.addItem(line)
        
        # Blacklist
        if hasattr(tab, 'blacklist_list_widget'):
            tab.blacklist_list_widget.clear()
            blacklist_lines = file_manager.read_text_file(str(Path(self.server_root) / 'blacklist.txt'))
            for line in blacklist_lines:
                tab.blacklist_list_widget.addItem(line)
    
    def clear_all_fields(self):
        """Clear all fields when no server is selected"""
        # Server config
        widgets = self.server_config_tab.server_config_widgets if self.server_config_tab else {}
        if widgets:
            widgets.get('NAME', type('', (), {'setText': lambda x: None})()).setText('')
            widgets.get('TRACK', type('', (), {'setText': lambda x: None})()).setText('')
            widgets.get('UDP_PORT', type('', (), {'setText': lambda x: None})()).setText('')
            widgets.get('TCP_PORT', type('', (), {'setText': lambda x: None})()).setText('')
            widgets.get('HTTP_PORT', type('', (), {'setText': lambda x: None})()).setText('')
            widgets.get('SERVER_DESCRIPTION', type('', (), {'setPlainText': lambda x: None})()).setPlainText('')
        
        # Entry list
        self.entry_list_data = []
        if self.server_config_tab and hasattr(self.server_config_tab, 'entry_list_table'):
            self.server_config_tab.entry_list_table.setRowCount(0)
        
        # Virtual Steward
        if self.virtual_steward_tab:
            self.virtual_steward_tab.vs_enabled_checkbox.setChecked(False)
            self.virtual_steward_tab.loop_lap_input.setText('')
            self.virtual_steward_tab.bot_trains_checkbox.setChecked(False)
            self.virtual_steward_tab.train_gap_slider.setValue(5)
            self.virtual_steward_tab.train_gap_value_label.setText('5')
            self.update_num_bots_combo_range(set_value=0)
        
        # Advanced options
        if self.advanced_options_tab:
            self.advanced_options_tab.weather_dropdown.setCurrentIndex(0)
            self.advanced_options_tab.force_headlights_checkbox.setChecked(False)
            self.advanced_options_tab.tires_allowed_dropdown.setCurrentIndex(0)
            self.advanced_options_tab.loading_image_url_input.setText('')
            self.advanced_options_tab.client_send_interval_input.setText('')
            self.advanced_options_tab.player_loading_timeout_input.setText('')
            self.advanced_options_tab.admins_list_widget.clear()
            self.advanced_options_tab.blacklist_list_widget.clear()
        
        self.configs = {}
        self.has_unsaved_changes = False
    
    def update_num_bots_combo_range(self, set_value=None):
        """Update num bots combo range"""
        if not self.virtual_steward_tab:
            return
        
        num_entries = len(self.entry_list_data)
        max_bots = max(0, num_entries - 1)
        
        current_val = set_value if set_value is not None else int(self.virtual_steward_tab.num_bots_combo.currentText() or '0')
        capped_val = min(current_val, max_bots)
        
        self.virtual_steward_tab.num_bots_combo.blockSignals(True)
        self.virtual_steward_tab.num_bots_combo.clear()
        for i in range(max_bots + 1):
            self.virtual_steward_tab.num_bots_combo.addItem(str(i))
        self.virtual_steward_tab.num_bots_combo.setCurrentIndex(capped_val)
        self.virtual_steward_tab.num_bots_combo.blockSignals(False)
    
    def on_num_bots_changed(self):
        """Handle number of bots change"""
        vs_enabled = self.virtual_steward_tab.vs_enabled_checkbox.isChecked()
        try:
            num_bots = int(self.virtual_steward_tab.num_bots_combo.currentText())
        except ValueError:
            num_bots = 0
        
        self._apply_vs_skins_to_entry_list(vs_enabled, num_bots)
        self.refresh_entry_list_table()
        self.mark_as_modified()
    
    def _apply_vs_skins_to_entry_list(self, vs_enabled: bool, num_bots: int):
        """
        Apply Virtual Steward skin modifications to entry list.
        
        When Virtual Steward is enabled, bot entries (first N entries) need the '/VS'
        skin suffix. This method handles the common logic for updating skins and GUIDs
        across both real-time changes (on_num_bots_changed) and file saves (save_config).
        
        Args:
            vs_enabled: Whether Virtual Steward is currently enabled
            num_bots: Number of bot entries (first N entries in the list)
        """
        for i, entry_data in enumerate(self.entry_list_data):
            if vs_enabled and i < num_bots:
                # Bot entry - add /VS suffix if not present
                skin = entry_data.get('skin', '')
                if not skin.endswith('/VS'):
                    entry_data['skin'] = skin + '/VS'
                entry_data['guid'] = str(8888880 + i)
            else:
                # Regular player entry - remove /VS suffix if present
                skin = entry_data.get('skin', '')
                if skin.endswith('/VS'):
                    entry_data['skin'] = skin[:-3]
                entry_data['guid'] = ''
    
    def on_vs_enabled_changed(self):
        """Enable/disable Virtual Steward controls"""
        is_checked = self.virtual_steward_tab.vs_enabled_checkbox.isChecked()
        
        controls = [
            'add_replay_btn',
            'lap_label',
            'loop_lap_input',
            'bot_trains_checkbox',
            'gap_label',
            'train_gap_slider',
            'train_gap_value_label',
            'num_bots_label',
            'num_bots_combo'
        ]
        
        for control_name in controls:
            if hasattr(self.virtual_steward_tab, control_name):
                getattr(self.virtual_steward_tab, control_name).setEnabled(is_checked)
        
        # Update replay file status display when VS is toggled
        if is_checked and self.server_root:
            self.virtual_steward_tab.update_replay_file_status()
        else:
            # Clear the replay file status when VS is disabled
            if hasattr(self.virtual_steward_tab, 'replay_file_status_label'):
                self.virtual_steward_tab.replay_file_status_label.setText("")
    
    def refresh_entry_list_table(self):
        """Refresh entry list table display"""
        table = self.server_config_tab.entry_list_table
        table.setRowCount(0)
        
        vs_enabled = self.virtual_steward_tab.vs_enabled_checkbox.isChecked()
        num_bots = 0
        if vs_enabled:
            try:
                num_bots = int(self.virtual_steward_tab.num_bots_combo.currentText())
            except ValueError:
                num_bots = 0

        for i, entry in enumerate(self.entry_list_data):
            model = entry['model']
            skin = entry['skin']

            table.insertRow(i)
            table.setRowHeight(i, 80)

            is_bot_entry = vs_enabled and i < num_bots

            # Model item
            model_item = QTableWidgetItem(format_display_string(model))
            model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
            if is_bot_entry:
                bold_font = QFont()
                bold_font.setBold(True)
                model_item.setFont(bold_font)
                model_item.setForeground(QBrush(QColor(0, 128, 0)))
            table.setItem(i, 0, model_item)

            # Skin item
            display_skin = skin[:-3] if skin.endswith('/VS') else skin
            skin_item = QTableWidgetItem(format_display_string(display_skin))
            skin_item.setFlags(skin_item.flags() & ~Qt.ItemIsEditable)
            if is_bot_entry:
                bold_font = QFont()
                bold_font.setBold(True)
                skin_item.setFont(bold_font)
                skin_item.setForeground(QBrush(QColor(0, 128, 0)))
            table.setItem(i, 1, skin_item)

            # Preview image
            if model and skin and self.content_root:
                actual_skin = skin[:-3] if skin.endswith('/VS') else skin
                preview_path = Path(self.content_root) / "cars" / model / "skins" / actual_skin / "preview.jpg"
                if preview_path.exists():
                    pixmap = QPixmap(str(preview_path))
                    if not pixmap.isNull():
                        scaled = pixmap.scaledToHeight(75, Qt.SmoothTransformation)
                        preview_item = QTableWidgetItem()
                        preview_item.setData(Qt.DecorationRole, scaled)
                        preview_item.setFlags(preview_item.flags() & ~Qt.ItemIsEditable)
                        table.setItem(i, 2, preview_item)
    
    def on_add_entry(self):
        """Add entry to list"""
        if not self.available_cars:
            QMessageBox.warning(self, "No Cars Found", "Please select a valid AC Content Root folder first.")
            return
        
        from dialogs import CarSelectionDialog
        car_dialog = CarSelectionDialog(self.available_cars, self)
        if car_dialog.exec_() and car_dialog.selected_car:
            selected_car = car_dialog.selected_car
            skins = file_manager.get_car_skins(self.content_root, selected_car)
            first_skin = skins[0] if skins else ''
            
            self.add_entry_to_list(selected_car, first_skin)
            self.mark_as_modified()
    
    def on_remove_entry(self):
        """Remove entry from list"""
        table = self.server_config_tab.entry_list_table
        rows = sorted(
            {idx.row() for idx in table.selectionModel().selectedRows()},
            reverse=True
        )
        if not rows:
            QMessageBox.warning(self, "No Selection", "Please select an entry to remove.")
            return
        for row in rows:
            if row < len(self.entry_list_data):
                self.entry_list_data.pop(row)
        self.update_num_bots_combo_range()
        self.refresh_entry_list_table()
        self.mark_as_modified()
    
    def on_duplicate_entry(self):
        """Duplicate entry"""
        table = self.server_config_tab.entry_list_table
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an entry to duplicate.")
            return
        
        row = selected_rows[0].row()
        
        if row < len(self.entry_list_data):
            selected_entry = self.entry_list_data[row]
            
            new_entry = {
                'section': f'CAR_{len(self.entry_list_data)}',
                'model': selected_entry.get('model', ''),
                'skin': selected_entry.get('skin', ''),
                'spectator_mode': selected_entry.get('spectator_mode', '0'),
                'drivername': selected_entry.get('drivername', ''),
                'team': selected_entry.get('team', ''),
                'guid': selected_entry.get('guid', ''),
                'ballast': selected_entry.get('ballast', '0'),
                'restrictor': selected_entry.get('restrictor', '0')
            }
            
            self.entry_list_data.append(new_entry)
        
        self.update_num_bots_combo_range()
        self.refresh_entry_list_table()
        self.mark_as_modified()
    
    def on_entry_list_reordered(self, src_row: int, dest_row: int):
        """Handle entry list reordering"""
        if src_row == dest_row or src_row < 0 or dest_row < 0:
            return
        if src_row >= len(self.entry_list_data) or dest_row >= len(self.entry_list_data):
            return

        entry = self.entry_list_data.pop(src_row)
        self.entry_list_data.insert(dest_row, entry)

        self.update_num_bots_combo_range()
        self.refresh_entry_list_table()

        self.server_config_tab.entry_list_table.selectRow(dest_row)
        self.mark_as_modified()
    
    def add_entry_to_list(self, model: str, skin: str):
        """Add entry to list"""
        self.entry_list_data.append({
            'section': f'CAR_{len(self.entry_list_data)}',
            'model': model,
            'skin': skin,
            'spectator_mode': '0',
            'drivername': '',
            'team': '',
            'guid': '',
            'ballast': '0',
            'restrictor': '0'
        })
        self.update_num_bots_combo_range()
        self.refresh_entry_list_table()
        new_row = self.server_config_tab.entry_list_table.rowCount() - 1
        self.server_config_tab.entry_list_table.selectRow(new_row)
    
    def save_config(self):
        """
        Persist all server and plugin configurations to disk.
        
        This method orchestrates a complex multi-file save workflow:
        1. Validates user input (required fields, numeric constraints)
        2. Writes to server_cfg.ini (core server settings: name, track, ports, weather)
        3. Writes to entry_list.ini (player and bot list with VS plugin modifications)
        4. Writes to plugin YAML configs (VS replay plugin, extra_cfg.yml)
        5. Writes to text files (admins.txt, blacklist.txt, whitelist.txt)
        6. Reloads configs from disk to sync UI state with saved files
        
        VS Integration:
        - When Virtual Steward is enabled, adds/removes '/VS' skin suffix on bot entries
        - Updates EnablePlugins list to include 'VSReplayPlugin'
        - Persists bot train settings (AutoStartOffset, etc.) to plugin config
        
        Error Handling:
        - Collects all errors without stopping, shows aggregated error message
        - Prevents config reload if any save operation fails
        - Returns early if no config is loaded
        """
        if not self.configs:
            QMessageBox.warning(self, "Warning", "No configuration loaded")
            return
        
        errors = []
        
        try:
            # Construct cfg path from current server_root
            cfg_path = Path(self.server_root) / "cfg"
            
            # Save server_cfg.ini
            server_cfg_path = cfg_path / "server_cfg.ini"
            if server_cfg_path.exists():
                try:
                    config_path = str(server_cfg_path)

                    # Validate required fields
                    if not self.server_config_tab.server_config_widgets['NAME'].text().strip():
                        errors.append("Server Name is required")
                    
                    if not self.server_config_tab.server_config_widgets['TRACK'].text().strip():
                        errors.append("Track is required")
                    
                    # Validate port numbers
                    try:
                        int(self.server_config_tab.server_config_widgets['UDP_PORT'].text().strip() or "0")
                    except ValueError:
                        errors.append("UDP Port must be a valid number")
                    
                    try:
                        int(self.server_config_tab.server_config_widgets['TCP_PORT'].text().strip() or "0")
                    except ValueError:
                        errors.append("TCP Port must be a valid number")
                    
                    try:
                        int(self.server_config_tab.server_config_widgets['HTTP_PORT'].text().strip() or "0")
                    except ValueError:
                        errors.append("HTTP Port must be a valid number")
                    
                    if errors:
                        raise ValueError("\n".join(errors))

                    # Resolve track value
                    track_display = self.server_config_tab.server_config_widgets['TRACK'].text()
                    if track_display in self.track_display_map:
                        track_value = self.track_display_map[track_display]
                    else:
                        track_value = track_display.lower().replace(' ', '_')

                    # SUN_ANGLE calculation
                    tod_str = self.server_config_tab.server_config_widgets['TIME_OF_DAY'].currentText()
                    sun_angle = int(tod_str) * 0.15 - 135
                    sun_angle_str = str(int(sun_angle)) if sun_angle == int(sun_angle) else f'{sun_angle:.1f}'

                    server_keys = {
                        'NAME': self.server_config_tab.server_config_widgets['NAME'].text(),
                        'TRACK': track_value,
                        'UDP_PORT': self.server_config_tab.server_config_widgets['UDP_PORT'].text(),
                        'TCP_PORT': self.server_config_tab.server_config_widgets['TCP_PORT'].text(),
                        'HTTP_PORT': self.server_config_tab.server_config_widgets['HTTP_PORT'].text(),
                        'TIME_OF_DAY_MULT': '1' if self.server_config_tab.server_config_widgets['TIME_OF_DAY_MULT'].isChecked() else '0',
                        'SUN_ANGLE': sun_angle_str,
                        'MAX_CLIENTS': str(len(self.entry_list_data)),
                    }
                    if hasattr(self.advanced_options_tab, 'tires_allowed_dropdown'):
                        server_keys['ALLOWED_TYRES_OUT'] = self.advanced_options_tab.tires_allowed_dropdown.currentText()
                    if hasattr(self.advanced_options_tab, 'client_send_interval_input'):
                        hz = self.advanced_options_tab.client_send_interval_input.text().strip()
                        server_keys['CLIENT_SEND_INTERVAL_HZ'] = hz if hz else '33'

                    section_updates = {'SERVER': server_keys}

                    if hasattr(self.advanced_options_tab, 'weather_dropdown'):
                        weather_text = self.advanced_options_tab.weather_dropdown.currentText()
                        if weather_text:
                            # Update with selected weather
                            section_updates['WEATHER_0'] = {'GRAPHICS': weather_text}

                    config_manager.save_ini_targeted(config_path, section_updates)
                except Exception as e:
                    errors.append(f"Server Configuration (server_cfg.ini): {str(e)}")
            
            # Save entry_list.ini
            entry_list_path = cfg_path / "entry_list.ini"
            if entry_list_path.exists():
                try:
                    config_path = str(entry_list_path)
                    
                    vs_checked = self.virtual_steward_tab.vs_enabled_checkbox.isChecked()
                    
                    if vs_checked:
                        num_bots = 0
                        try:
                            num_bots = int(self.virtual_steward_tab.num_bots_combo.currentText())
                        except ValueError:
                            num_bots = 0
                    else:
                        num_bots = 0
                    
                    # Apply VS skin modifications to all entries
                    self._apply_vs_skins_to_entry_list(vs_checked, num_bots)
                    
                    config_manager.write_entry_list_ini(config_path, self.entry_list_data)
                    self.update_num_bots_combo_range()
                    self.refresh_entry_list_table()
                except Exception as e:
                    errors.append(f"Entry List (entry_list.ini): {str(e)}")

            
            # Save extra_cfg.yml
            extra_cfg_path = cfg_path / "extra_cfg.yml"
            if extra_cfg_path.exists():
                try:
                    config_path = str(extra_cfg_path)

                    scalar_updates = {}

                    if 'SERVER_DESCRIPTION' in self.server_config_tab.server_config_widgets:
                        scalar_updates['ServerDescription'] = (
                            self.server_config_tab.server_config_widgets['SERVER_DESCRIPTION'].toPlainText()
                        )

                    if hasattr(self.advanced_options_tab, 'force_headlights_checkbox'):
                        scalar_updates['ForceLights'] = self.advanced_options_tab.force_headlights_checkbox.isChecked()

                    if hasattr(self.advanced_options_tab, 'loading_image_url_input'):
                        url_text = self.advanced_options_tab.loading_image_url_input.text().strip()
                        scalar_updates['LoadingImageUrls'] = [url_text] if url_text else None

                    if hasattr(self.advanced_options_tab, 'player_loading_timeout_input'):
                        timeout_text = self.advanced_options_tab.player_loading_timeout_input.text().strip()
                        try:
                            scalar_updates['PlayerLoadingTimeoutMinutes'] = (
                                int(timeout_text) if timeout_text else 10
                            )
                        except ValueError:
                            errors.append("Player Loading Timeout must be a valid number")
                            raise ValueError("Player Loading Timeout is invalid")

                    enable_plugins = None
                    if hasattr(self.virtual_steward_tab, 'vs_enabled_checkbox'):
                        existing_plugins = list(
                            self.configs['extra_cfg.yml'].get('data', {}).get('EnablePlugins') or []
                        )
                        vs_is_enabled = self.virtual_steward_tab.vs_enabled_checkbox.isChecked()
                        vs_is_in_list = 'VSReplayPlugin' in existing_plugins
                        
                        # Only update EnablePlugins if there's a change
                        if vs_is_enabled and not vs_is_in_list:
                            # Need to add VSReplayPlugin
                            enable_plugins = existing_plugins + ['VSReplayPlugin']
                        elif not vs_is_enabled and vs_is_in_list:
                            # Need to remove VSReplayPlugin
                            enable_plugins = [p for p in existing_plugins if p != 'VSReplayPlugin']
                        # If no change needed, enable_plugins stays None and won't be updated

                    config_manager.save_yaml_targeted(config_path, scalar_updates, enable_plugins)
                except Exception as e:
                    if "Player Loading Timeout" not in str(e):
                        errors.append(f"Server Extra Configuration (extra_cfg.yml): {str(e)}")
            
            # Save plugin_vs_replay_cfg.yml
            plugin_cfg_path = cfg_path / "plugin_vs_replay_cfg.yml"
            if plugin_cfg_path.exists():
                try:
                    config_path = str(plugin_cfg_path)

                    scalar_updates = {}

                    if hasattr(self.virtual_steward_tab, 'bot_trains_checkbox') and hasattr(self.virtual_steward_tab, 'train_gap_slider'):
                        scalar_updates['AutoStartOffset'] = (
                            self.virtual_steward_tab.train_gap_slider.value() if self.virtual_steward_tab.bot_trains_checkbox.isChecked() else 0
                        )

                    if hasattr(self.virtual_steward_tab, 'num_bots_combo'):
                        try:
                            scalar_updates['AutoStart'] = int(self.virtual_steward_tab.num_bots_combo.currentText())
                        except ValueError:
                            errors.append("Number of Bots must be a valid number")
                            raise ValueError("Number of Bots is invalid")

                    if hasattr(self.virtual_steward_tab, 'loop_lap_input'):
                        loop_lap_text = self.virtual_steward_tab.loop_lap_input.text().strip()
                        if loop_lap_text:
                            try:
                                scalar_updates['LoopLap'] = int(loop_lap_text)
                            except ValueError:
                                errors.append("Loop Lap must be a valid number")
                                raise ValueError("Loop Lap is invalid")
                        else:
                            scalar_updates['LoopLap'] = ''

                    config_manager.save_yaml_targeted(config_path, scalar_updates)
                except Exception as e:
                    if "Loop Lap" not in str(e) and "Number of Bots" not in str(e):
                        errors.append(f"Virtual Steward Configuration (plugin_vs_replay_cfg.yml): {str(e)}")
            
            # Update data_track_params.ini
            cfg_path = Path(self.server_root) / "cfg"
            data_track_params_path = cfg_path / "data_track_params.ini"
            if data_track_params_path.exists():
                try:
                    track_input = self.server_config_tab.server_config_widgets['TRACK']
                    track_value = track_input.property('original_track')
                    
                    if not track_value:
                        track_display = track_input.text()
                        if track_display in self.track_display_map:
                            track_value = self.track_display_map[track_display]
                        else:
                            track_value = track_display.lower().replace(' ', '_')
                    
                    # Note: data_track_params.ini should NOT be modified - it contains all track configs
                    # The AC server reads the section matching the TRACK value in server_cfg.ini
                    # config_manager.update_data_track_params(data_track_params_path, track_value)
                except Exception as e:
                    errors.append(f"Track Parameters (data_track_params.ini): {str(e)}")
            
            # Save admins.txt and blacklist.txt
            server_root = Path(self.server_root)
            
            if hasattr(self.advanced_options_tab, 'admins_list_widget'):
                try:
                    admins_entries = []
                    for i in range(self.advanced_options_tab.admins_list_widget.count()):
                        item = self.advanced_options_tab.admins_list_widget.item(i)
                        if item:
                            admins_entries.append(item.text())
                    file_manager.write_text_file(str(server_root / 'admins.txt'), admins_entries)
                except Exception as e:
                    errors.append(f"Admins List: {str(e)}")
            
            if hasattr(self.advanced_options_tab, 'blacklist_list_widget'):
                try:
                    blacklist_entries = []
                    for i in range(self.advanced_options_tab.blacklist_list_widget.count()):
                        item = self.advanced_options_tab.blacklist_list_widget.item(i)
                        if item:
                            blacklist_entries.append(item.text())
                    file_manager.write_text_file(str(server_root / 'blacklist.txt'), blacklist_entries)
                except Exception as e:
                    errors.append(f"Blacklist: {str(e)}")
            
            if errors:
                error_message = "Some configurations could not be saved:\n\n" + "\n".join(errors)
                QMessageBox.critical(self, "Save Error", error_message)
            else:
                # Reload configs to reflect saved changes for next save operation
                try:
                    self.configs = config_manager.load_configs(self.server_root)
                except Exception as e:
                    pass  # Non-critical if reload fails
                
                QMessageBox.information(self, "Success", "All configurations saved successfully")
                self.has_unsaved_changes = False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
    
    def mark_as_modified(self):
        """Mark that there are unsaved changes"""
        self.has_unsaved_changes = True
    
    def launch_server(self):
        """Launch the server"""
        if not self.server_root:
            QMessageBox.warning(self, "Warning", "Please select a server folder first")
            return
        
        if self.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Would you like to save before launching?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Save:
                self.save_config()
                if self.has_unsaved_changes:
                    return
        
        server_root_path = Path(self.server_root)
        server_exe = server_root_path / "AssettoServer.exe"
        
        if not server_exe.exists():
            QMessageBox.critical(self, "Error", f"AssettoServer.exe not found at:\n{server_exe}")
            return
        
        try:
            server_name = server_root_path.name
            console_title = server_name

            wt_result = subprocess.run(
                ['where', 'wt.exe'],
                capture_output=True, text=True
            )
            if wt_result.returncode == 0:
                subprocess.Popen(
                    [
                        'wt.exe', '-w', '0', 'new-tab',
                        '--title', console_title,
                        '--suppressApplicationTitle',
                        '--startingDirectory', str(server_root_path),
                        'cmd', '/k', str(server_exe)
                    ]
                )
            else:
                si = subprocess.STARTUPINFO()
                si.lpTitle = console_title
                subprocess.Popen(
                    ['cmd', '/k', str(server_exe)],
                    cwd=str(server_root_path),
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    startupinfo=si
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch server:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Kill all running servers
        if self.main_menu_tab:
            self.main_menu_tab.kill_all_servers()
        
        if self.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Would you like to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if result == QMessageBox.Cancel:
                event.ignore()
                return
            elif result == QMessageBox.Save:
                self.save_config()
                if self.has_unsaved_changes:
                    event.ignore()
                    return
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    icon_path = get_resource_path("files/Icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = ACServerConfigGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()