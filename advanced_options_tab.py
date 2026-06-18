"""
Advanced Options Tab for the Assetto Corsa Server Configuration Manager
Handles weather, headlights, admin lists, and logging options
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QCheckBox, QListWidget, QListWidgetItem, QMessageBox, QDialog,
    QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from pathlib import Path
import subprocess

import file_manager


class AdvancedOptionsTab(QWidget):
    """Advanced Options Tab with weather, admins, blacklist, and logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize the Advanced Options tab UI"""
        layout = QVBoxLayout()
        
        label = QLabel("Advanced Options")
        label_font = label.font()
        label_font.setPointSize(12)
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        # Weather Option
        weather_row = QHBoxLayout()
        weather_row.addWidget(QLabel("Weather:"))
        
        self.weather_dropdown = QComboBox()
        self.weather_dropdown.currentIndexChanged.connect(self.parent_window.mark_as_modified)
        weather_row.addWidget(self.weather_dropdown)
        weather_row.addStretch()
        
        layout.addLayout(weather_row)
        
        # Force Headlights Option
        force_lights_row = QHBoxLayout()
        self.force_headlights_checkbox = QCheckBox("Force Headlights")
        self.force_headlights_checkbox.stateChanged.connect(self.parent_window.mark_as_modified)
        force_lights_row.addWidget(self.force_headlights_checkbox)
        force_lights_row.addStretch()
        
        layout.addLayout(force_lights_row)
        
        # Tires Allowed Out Option
        tires_row = QHBoxLayout()
        tires_row.addWidget(QLabel("Tires Allowed Out:"))
        
        self.tires_allowed_dropdown = QComboBox()
        self.tires_allowed_dropdown.addItems(["0", "1", "2", "3", "4"])
        self.tires_allowed_dropdown.currentIndexChanged.connect(self.parent_window.mark_as_modified)
        tires_row.addWidget(self.tires_allowed_dropdown)
        tires_row.addStretch()
        
        layout.addLayout(tires_row)
        
        # Custom Loading Screen Image URL
        url_row = QHBoxLayout()
        url_row.addWidget(QLabel("Custom Loading Screen Image URL:"))
        
        self.loading_image_url_input = QLineEdit()
        self.loading_image_url_input.textChanged.connect(self.parent_window.mark_as_modified)
        url_row.addWidget(self.loading_image_url_input)
        
        layout.addLayout(url_row)
        
        # Client Send Interval HZ
        hz_row = QHBoxLayout()
        hz_row.addWidget(QLabel("Client Send Interval HZ:"))
        
        self.client_send_interval_input = QLineEdit()
        self.client_send_interval_input.setMaximumWidth(100)
        self.client_send_interval_input.textChanged.connect(self.parent_window.mark_as_modified)
        hz_row.addWidget(self.client_send_interval_input)
        hz_row.addStretch()
        
        layout.addLayout(hz_row)
        
        # Player Loading Timeout Minutes
        timeout_row = QHBoxLayout()
        timeout_row.addWidget(QLabel("Player Loading Timeout Minutes:"))
        
        self.player_loading_timeout_input = QLineEdit()
        self.player_loading_timeout_input.setMaximumWidth(100)
        self.player_loading_timeout_input.textChanged.connect(self.parent_window.mark_as_modified)
        timeout_row.addWidget(self.player_loading_timeout_input)
        timeout_row.addStretch()
        
        layout.addLayout(timeout_row)
        
        # Admins and Blacklist side-by-side
        lists_container = QHBoxLayout()
        
        # ========== ADMINS SECTION ==========
        admins_column = QVBoxLayout()
        
        admins_label = QLabel("Admins")
        admins_label_font = admins_label.font()
        admins_label_font.setBold(True)
        admins_label.setFont(admins_label_font)
        admins_column.addWidget(admins_label)
        
        self.admins_list_widget = QListWidget()
        self.admins_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.admins_list_widget.itemSelectionChanged.connect(self.on_admins_selection_changed)
        admins_column.addWidget(self.admins_list_widget)
        
        # Buttons for Admins
        admins_button_row = QHBoxLayout()
        self.admins_add_button = QPushButton("Add")
        self.admins_add_button.clicked.connect(self.open_add_admin_dialog)
        admins_button_row.addWidget(self.admins_add_button)
        
        self.admins_remove_button = QPushButton("Remove")
        self.admins_remove_button.setEnabled(False)
        self.admins_remove_button.clicked.connect(self.remove_admin)
        admins_button_row.addWidget(self.admins_remove_button)
        
        admins_column.addLayout(admins_button_row)
        lists_container.addLayout(admins_column)
        
        # ========== BLACKLIST SECTION ==========
        blacklist_column = QVBoxLayout()
        
        blacklist_label = QLabel("Blacklist")
        blacklist_label_font = blacklist_label.font()
        blacklist_label_font.setBold(True)
        blacklist_label.setFont(blacklist_label_font)
        blacklist_column.addWidget(blacklist_label)
        
        self.blacklist_list_widget = QListWidget()
        self.blacklist_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.blacklist_list_widget.itemSelectionChanged.connect(self.on_blacklist_selection_changed)
        blacklist_column.addWidget(self.blacklist_list_widget)
        
        # Buttons for Blacklist
        blacklist_button_row = QHBoxLayout()
        self.blacklist_add_button = QPushButton("Add")
        self.blacklist_add_button.clicked.connect(self.open_add_blacklist_dialog)
        blacklist_button_row.addWidget(self.blacklist_add_button)
        
        self.blacklist_remove_button = QPushButton("Remove")
        self.blacklist_remove_button.setEnabled(False)
        self.blacklist_remove_button.clicked.connect(self.remove_blacklist)
        blacklist_button_row.addWidget(self.blacklist_remove_button)
        
        blacklist_column.addLayout(blacklist_button_row)
        lists_container.addLayout(blacklist_column)
        
        layout.addLayout(lists_container)
        
        # Buttons for opening logs folders
        logs_button_row = QHBoxLayout()
        
        self.open_crash_logs_button = QPushButton("Open Crash Logs")
        self.open_crash_logs_button.clicked.connect(self.open_crash_logs_folder)
        logs_button_row.addWidget(self.open_crash_logs_button)
        
        self.open_server_logs_button = QPushButton("Open Server Logs")
        self.open_server_logs_button.clicked.connect(self.open_server_logs_folder)
        logs_button_row.addWidget(self.open_server_logs_button)
        
        self.open_server_folder_button = QPushButton("Open Server Folder")
        self.open_server_folder_button.clicked.connect(self.open_server_folder)
        logs_button_row.addWidget(self.open_server_folder_button)
        
        layout.addLayout(logs_button_row)
        
        self.setLayout(layout)
    
    def open_add_admin_dialog(self):
        """Open dialog to add an admin entry"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Admin")
        dialog.setModal(True)
        dialog_layout = QVBoxLayout()
        
        label = QLabel("Enter admin entry:")
        dialog_layout.addWidget(label)
        
        text_input = QLineEdit()
        dialog_layout.addWidget(text_input)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        def on_ok_clicked():
            entry = text_input.text().strip()
            if entry:
                self.admins_list_widget.addItem(entry)
                self.parent_window.mark_as_modified()
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Empty Entry", "Please enter a value.")
        
        def on_cancel_clicked():
            dialog.reject()
        
        ok_button.clicked.connect(on_ok_clicked)
        cancel_button.clicked.connect(on_cancel_clicked)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        dialog_layout.addLayout(button_layout)
        
        dialog.setLayout(dialog_layout)
        dialog.setMinimumWidth(300)
        dialog.exec_()
    
    def open_add_blacklist_dialog(self):
        """Open dialog to add a blacklist entry"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Blacklist Entry")
        dialog.setModal(True)
        dialog_layout = QVBoxLayout()
        
        label = QLabel("Enter blacklist entry:")
        dialog_layout.addWidget(label)
        
        text_input = QLineEdit()
        dialog_layout.addWidget(text_input)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        def on_ok_clicked():
            entry = text_input.text().strip()
            if entry:
                self.blacklist_list_widget.addItem(entry)
                self.parent_window.mark_as_modified()
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Empty Entry", "Please enter a value.")
        
        def on_cancel_clicked():
            dialog.reject()
        
        ok_button.clicked.connect(on_ok_clicked)
        cancel_button.clicked.connect(on_cancel_clicked)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        dialog_layout.addLayout(button_layout)
        
        dialog.setLayout(dialog_layout)
        dialog.setMinimumWidth(300)
        dialog.exec_()
    
    def on_admins_selection_changed(self):
        """Enable/disable Remove button based on selection"""
        has_selection = len(self.admins_list_widget.selectedItems()) > 0
        self.admins_remove_button.setEnabled(has_selection)
    
    def on_blacklist_selection_changed(self):
        """Enable/disable Remove button based on selection"""
        has_selection = len(self.blacklist_list_widget.selectedItems()) > 0
        self.blacklist_remove_button.setEnabled(has_selection)
    
    def remove_admin(self):
        """Remove all selected admin entries"""
        for item in self.admins_list_widget.selectedItems():
            self.admins_list_widget.takeItem(self.admins_list_widget.row(item))
        self.parent_window.mark_as_modified()
    
    def remove_blacklist(self):
        """Remove all selected blacklist entries"""
        for item in self.blacklist_list_widget.selectedItems():
            self.blacklist_list_widget.takeItem(self.blacklist_list_widget.row(item))
        self.parent_window.mark_as_modified()
    
    def open_crash_logs_folder(self):
        """Open the crash logs folder in Windows Explorer"""
        crash_folder = Path(self.parent_window.server_root) / "crash"
        if crash_folder.exists():
            try:
                subprocess.Popen(['explorer', str(crash_folder)])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open crash logs folder: {str(e)}")
        else:
            QMessageBox.warning(self, "Folder Not Found", f"Crash logs folder not found at:\n{crash_folder}")
    
    def open_server_logs_folder(self):
        """Open the server logs folder in Windows Explorer"""
        logs_folder = Path(self.parent_window.server_root) / "logs"
        if logs_folder.exists():
            try:
                subprocess.Popen(['explorer', str(logs_folder)])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open server logs folder: {str(e)}")
        else:
            QMessageBox.warning(self, "Folder Not Found", f"Server logs folder not found at:\n{logs_folder}")
    
    def open_server_folder(self):
        """Open the server folder in Windows Explorer"""
        if not self.parent_window.server_root:
            QMessageBox.warning(self, "No Server Selected", "Please select a server folder first.")
            return
        
        server_folder = Path(self.parent_window.server_root)
        if server_folder.exists():
            try:
                subprocess.Popen(['explorer', str(server_folder)])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open server folder: {str(e)}")
        else:
            QMessageBox.warning(self, "Folder Not Found", f"Server folder not found at:\n{server_folder}")
