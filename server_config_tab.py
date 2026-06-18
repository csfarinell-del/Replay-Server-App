"""
Server Configuration Tab for the Assetto Corsa Server Configuration Manager
Handles server info editing and entry list management
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, 
    QComboBox, QPlainTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from widgets import ClickableLineEdit, EntryListTable
from dialogs import CarSelectionDialog, SkinSelectionDialog, TrackSelectionDialog
import file_manager


class ServerConfigTab(QWidget):
    """Server Configuration tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.server_config_widgets = {}
        self.entry_list_table = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)
        
        # LEFT SIDE: Server config form
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Server Information title
        info_title = QLabel("Server Information")
        info_font = QFont()
        info_font.setPointSize(12)
        info_font.setBold(True)
        info_title.setFont(info_font)
        left_layout.addWidget(info_title, 0)
        
        # Form fields in scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        scroll_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(5)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Server Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Server Name:"))
        self.server_config_widgets['NAME'] = QLineEdit()
        name_layout.addWidget(self.server_config_widgets['NAME'])
        form_layout.addLayout(name_layout)
        
        # Track
        track_layout = QHBoxLayout()
        track_layout.addWidget(QLabel("Track:"))
        self.server_config_widgets['TRACK'] = ClickableLineEdit()
        self.server_config_widgets['TRACK'].setReadOnly(True)
        self.server_config_widgets['TRACK'].doubleClicked.connect(self.open_track_selection)
        track_layout.addWidget(self.server_config_widgets['TRACK'])
        form_layout.addLayout(track_layout)
        
        # Ports
        ports_layout = QHBoxLayout()
        ports_layout.addWidget(QLabel("UDP Port:"))
        self.server_config_widgets['UDP_PORT'] = QLineEdit()
        ports_layout.addWidget(self.server_config_widgets['UDP_PORT'])
        ports_layout.addWidget(QLabel("TCP Port:"))
        self.server_config_widgets['TCP_PORT'] = QLineEdit()
        ports_layout.addWidget(self.server_config_widgets['TCP_PORT'])
        ports_layout.addWidget(QLabel("HTTP Port:"))
        self.server_config_widgets['HTTP_PORT'] = QLineEdit()
        ports_layout.addWidget(self.server_config_widgets['HTTP_PORT'])
        form_layout.addLayout(ports_layout)
        
        # Time of day
        time_layout = QHBoxLayout()
        self.server_config_widgets['TIME_OF_DAY_MULT'] = QCheckBox("Time of Day (Dynamic)")
        time_layout.addWidget(self.server_config_widgets['TIME_OF_DAY_MULT'])
        time_layout.addWidget(QLabel("Time:"))
        self.server_config_widgets['TIME_OF_DAY'] = QComboBox()
        self.server_config_widgets['TIME_OF_DAY'].addItems(['0000', '0300', '0600', '0900', '1200', '1500', '1800', '2100'])
        time_layout.addWidget(self.server_config_widgets['TIME_OF_DAY'])
        time_layout.addStretch()
        form_layout.addLayout(time_layout)
        
        form_layout.addStretch()
        scroll_widget.setLayout(form_layout)
        scroll_area.setWidget(scroll_widget)
        left_layout.addWidget(scroll_area, 0)
        
        # Server Description
        left_layout.addWidget(QLabel("Server Description:"), 0)
        self.server_config_widgets['SERVER_DESCRIPTION'] = QPlainTextEdit()
        left_layout.addWidget(self.server_config_widgets['SERVER_DESCRIPTION'], 1)
        
        # Save Changes button (left-aligned)
        save_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self.parent_window.save_config)
        save_layout.addWidget(save_btn)
        save_layout.addStretch()
        left_layout.addLayout(save_layout, 0)
        
        main_layout.addLayout(left_layout, 1)
        
        # RIGHT SIDE: Entry list
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)
        
        # Entry List title
        entry_title = QLabel("Entry List")
        entry_font = QFont()
        entry_font.setPointSize(12)
        entry_font.setBold(True)
        entry_title.setFont(entry_font)
        right_layout.addWidget(entry_title, 0)
        
        # Table
        self.entry_list_table = EntryListTable()
        self.entry_list_table.setColumnCount(3)
        self.entry_list_table.setHorizontalHeaderLabels(["Model", "Skin", "Preview"])
        self.entry_list_table.setColumnWidth(0, 150)
        self.entry_list_table.setColumnWidth(1, 150)
        self.entry_list_table.setColumnWidth(2, 200)
        self.entry_list_table.cellDoubleClicked.connect(self.on_entry_double_clicked)
        self.entry_list_table.rowDropped.connect(self.parent_window.on_entry_list_reordered)
        self.entry_list_table.selectionModel().selectionChanged.connect(self.on_entry_selection_changed)
        
        right_layout.addWidget(self.entry_list_table, 1)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Entry")
        add_btn.clicked.connect(self.parent_window.on_add_entry)
        buttons_layout.addWidget(add_btn)
        
        self.remove_btn = QPushButton("Remove Entry")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.parent_window.on_remove_entry)
        buttons_layout.addWidget(self.remove_btn)
        
        self.duplicate_btn = QPushButton("Duplicate Entry")
        self.duplicate_btn.setEnabled(False)
        self.duplicate_btn.clicked.connect(self.parent_window.on_duplicate_entry)
        buttons_layout.addWidget(self.duplicate_btn)
        
        right_layout.addLayout(buttons_layout, 0)
        
        main_layout.addLayout(right_layout, 1)
        
        self.setLayout(main_layout)
    
    def on_entry_double_clicked(self, row: int, col: int):
        """Handle entry list double-click"""
        if not self.parent_window.content_root:
            QMessageBox.warning(self, "Error", "Please select AC content root first")
            return
        
        if row < len(self.parent_window.entry_list_data):
            entry = self.parent_window.entry_list_data[row]
            
            if col == 0:  # Model column
                # Open car selection dialog
                dialog = CarSelectionDialog(self.parent_window.available_cars, self)
                if dialog.exec_() and dialog.selected_car:
                    entry['model'] = dialog.selected_car
                    # Reset skin when changing car
                    skins = file_manager.get_car_skins(
                        self.parent_window.content_root, 
                        dialog.selected_car
                    )
                    entry['skin'] = skins[0] if skins else ''
                    self.parent_window.refresh_entry_list_table()
                    self.parent_window.mark_as_modified()
            
            elif col == 1 or col == 2:  # Skin column or preview
                # Open skin selection dialog
                if not entry['model']:
                    QMessageBox.warning(self, "Error", "Please select a car model first")
                    return
                
                skins = file_manager.get_car_skins(
                    self.parent_window.content_root,
                    entry['model']
                )
                if not skins:
                    QMessageBox.warning(self, "Error", f"No skins found for {entry['model']}")
                    return
                
                dialog = SkinSelectionDialog(skins, self.parent_window.content_root, entry['model'], self)
                if dialog.exec_() and dialog.selected_skin:
                    entry['skin'] = dialog.selected_skin
                    self.parent_window.refresh_entry_list_table()
                    self.parent_window.mark_as_modified()
    
    def open_track_selection(self):
        """Open track selection dialog"""
        if not self.parent_window.available_tracks:
            QMessageBox.warning(self, "Error", "Please select AC content root first")
            return
        
        dialog = TrackSelectionDialog(self.parent_window.available_tracks, self)
        if dialog.exec_() and dialog.selected_track:
            self.server_config_widgets['TRACK'].setText(dialog.selected_track)
            # Store original track name for saving
            if dialog.selected_track in self.parent_window.track_display_map.values():
                # It's already the original name
                original = dialog.selected_track
            elif dialog.selected_track in self.parent_window.track_display_map:
                # It's a display name
                original = self.parent_window.track_display_map[dialog.selected_track]
            else:
                # Fallback: convert display to original
                original = dialog.selected_track.lower().replace(' ', '_')
            
            self.server_config_widgets['TRACK'].setProperty('original_track', original)
            self.parent_window.mark_as_modified()
    
    def on_entry_selection_changed(self):
        """Handle entry selection change"""
        has_selection = len(self.entry_list_table.selectionModel().selectedRows()) > 0
        self.remove_btn.setEnabled(has_selection)
        self.duplicate_btn.setEnabled(has_selection)
