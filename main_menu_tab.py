"""
Main Menu Tab for the Assetto Corsa Server Configuration Manager
Handles folder selection and server management
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from widgets import PathLineEdit
import file_manager


class MainMenuTab(QWidget):
    """Main Menu tab for server and folder management"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout()
        
        # Main Menu title
        title_label = QLabel("Main Menu")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # AC Content Root section
        ac_root_layout = QHBoxLayout()
        ac_root_label = QLabel("AC Content Root:")
        self.ac_root_input = PathLineEdit()
        self.ac_root_input.setPlaceholderText("Path to AC content root folder...")
        self.ac_root_input.focusLost.connect(self.on_content_path_edited)
        ac_root_browse = QPushButton("Browse...")
        ac_root_browse.clicked.connect(self.browse_ac_root)
        
        ac_root_layout.addWidget(ac_root_label, 0)
        ac_root_layout.addWidget(self.ac_root_input, 1)
        ac_root_layout.addWidget(ac_root_browse, 0)
        main_layout.addLayout(ac_root_layout)
        
        # Server folder section
        server_root_layout = QHBoxLayout()
        server_root_label = QLabel("Server Folder (parent dir):")
        self.server_root_input = PathLineEdit()
        self.server_root_input.setPlaceholderText("Path to folder containing servers...")
        self.server_root_input.focusLost.connect(self.on_server_path_edited)
        server_root_browse = QPushButton("Browse...")
        server_root_browse.clicked.connect(self.browse_server_root)
        
        server_root_layout.addWidget(server_root_label, 0)
        server_root_layout.addWidget(self.server_root_input, 1)
        server_root_layout.addWidget(server_root_browse, 0)
        main_layout.addLayout(server_root_layout)
        
        # Servers list section
        list_label = QLabel("Available Servers:")
        list_font = QFont()
        list_font.setPointSize(12)
        list_font.setBold(True)
        list_label.setFont(list_font)
        main_layout.addWidget(list_label)
        
        self.servers_list = QListWidget()
        self.servers_list.itemClicked.connect(self.on_server_list_item_clicked)
        main_layout.addWidget(self.servers_list, 1)
        
        # Server management buttons
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Server")
        add_btn.clicked.connect(self.add_server)
        buttons_layout.addWidget(add_btn)
        
        duplicate_btn = QPushButton("Duplicate Server")
        duplicate_btn.clicked.connect(self.duplicate_server)
        buttons_layout.addWidget(duplicate_btn)
        
        rename_btn = QPushButton("Rename Server")
        rename_btn.clicked.connect(self.rename_server)
        buttons_layout.addWidget(rename_btn)
        
        delete_btn = QPushButton("Delete Server")
        delete_btn.clicked.connect(self.delete_server_folder)
        buttons_layout.addWidget(delete_btn)
        
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def browse_ac_root(self):
        """Browse for AC content root folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select AC Content Root Folder",
            self.ac_root_input.text() or ""
        )
        
        if folder:
            self.ac_root_input.setText(folder)
            self.on_content_path_edited()
    
    def browse_server_root(self):
        """Browse for server folder (parent directory)"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Server Folder (Parent Directory)",
            self.server_root_input.text() or ""
        )
        
        if folder:
            self.server_root_input.setText(folder)
            self.on_server_path_edited()
    
    def on_content_path_edited(self):
        """Handle AC content root path change"""
        path = self.ac_root_input.text().strip()
        
        if path and Path(path).exists():
            self.parent_window.content_root = path
            self.parent_window.on_content_discovery_changed()
            self.parent_window.settings.setValue('ac_content_root', path)
        elif not path:
            self.parent_window.content_root = None
    
    def on_server_path_edited(self):
        """Handle server folder path change"""
        path = self.server_root_input.text().strip()
        
        if path and Path(path).exists():
            self.parent_window.servers_parent_dir = path
            self.parent_window.settings.setValue('servers_parent_dir', path)
            self.populate_servers_list()
        elif not path:
            self.parent_window.servers_parent_dir = None
    
    def populate_servers_list(self):
        """Populate the servers list widget"""
        self.servers_list.clear()
        
        if not self.parent_window.servers_parent_dir:
            return
        
        servers = file_manager.list_server_directories(self.parent_window.servers_parent_dir)
        
        for server_name, server_path in servers:
            item = QListWidgetItem(server_name)
            item.setData(Qt.UserRole, server_path)
            self.servers_list.addItem(item)
    
    def on_server_list_item_clicked(self, item):
        """Handle server list item click"""
        # Check for unsaved changes
        if self.parent_window.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Save before switching servers?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Save:
                self.parent_window.save_config()
                if self.parent_window.has_unsaved_changes:
                    return
        
        server_path = item.data(Qt.UserRole)
        self.parent_window.server_root = server_path
        self.parent_window.settings.setValue('server_root', server_path)
        self.parent_window.auto_load_configs()
    
    def _select_server_in_list(self, server_path: str):
        """Select a server in the list by path"""
        for i in range(self.servers_list.count()):
            item = self.servers_list.item(i)
            if item.data(Qt.UserRole) == server_path:
                self.servers_list.setCurrentItem(item)
                break
    
    def add_server(self):
        """Add a new server from template"""
        if not self.parent_window.servers_parent_dir:
            QMessageBox.warning(self, "Error", "Please select a server folder first")
            return
        
        try:
            new_server_path = file_manager.copy_server_template(self.parent_window.servers_parent_dir)
            self.populate_servers_list()
            self._select_server_in_list(new_server_path)
            QMessageBox.information(self, "Success", f"Server created: {Path(new_server_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create server: {str(e)}")
    
    def duplicate_server(self):
        """Duplicate selected server"""
        selected = self.servers_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select a server to duplicate")
            return
        
        server_path = selected.data(Qt.UserRole)
        
        try:
            new_server_path = file_manager.duplicate_server(server_path, self.parent_window.servers_parent_dir)
            self.populate_servers_list()
            self._select_server_in_list(new_server_path)
            QMessageBox.information(self, "Success", f"Server duplicated: {Path(new_server_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to duplicate server: {str(e)}")
    
    def rename_server(self):
        """Rename selected server"""
        selected = self.servers_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select a server to rename")
            return
        
        old_path = selected.data(Qt.UserRole)
        old_name = Path(old_path).name
        
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Server",
            "Enter new server name:",
            text=old_name
        )
        
        if not ok or not new_name or new_name == old_name:
            return
        
        try:
            new_path = file_manager.rename_server_folder(old_path, new_name)
            self.parent_window.server_root = new_path
            self.parent_window.settings.setValue('server_root', new_path)
            self.populate_servers_list()
            self._select_server_in_list(new_path)
            QMessageBox.information(self, "Success", f"Server renamed to: {new_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename server: {str(e)}")
    
    def delete_server_folder(self):
        """Delete selected servers"""
        selected_items = self.servers_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select servers to delete")
            return
        
        # Confirm deletion
        count = len(selected_items)
        result = QMessageBox.warning(
            self,
            "Confirm Delete",
            f"Delete {count} server(s)? This cannot be undone.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        if result != QMessageBox.Ok:
            return
        
        # Delete servers
        paths = [item.data(Qt.UserRole) for item in selected_items]
        errors = file_manager.delete_server_folders(paths)
        
        # Clear current selection
        self.parent_window.server_root = None
        self.parent_window.clear_all_fields()
        
        self.populate_servers_list()
        
        if errors:
            QMessageBox.warning(self, "Errors", "\n".join(errors))
        else:
            QMessageBox.information(self, "Success", f"Deleted {count} server(s)")
