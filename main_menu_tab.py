"""
Main Menu Tab for the Assetto Corsa Server Configuration Manager
Handles folder selection and server management
Includes integrated terminal functionality for each server
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QInputDialog,
    QTextEdit, QSplitter, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QProcess, pyqtSignal
from PyQt5.QtGui import QFont

from widgets import PathLineEdit
import file_manager


class MainMenuTab(QWidget):
    """Main Menu tab for server and folder management with integrated terminal"""
    
    # Signal to communicate with main window about server status
    server_started = pyqtSignal()
    server_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Terminal history storage - one terminal per server
        self.server_terminals: Dict[str, QTextEdit] = {}  # path -> terminal widget
        self.current_server_path = None
        self.running_processes: Dict[str, QProcess] = {}  # path -> QProcess for running servers
        
        # Auto-scroll tracking
        self.terminal_auto_scroll_enabled = True
        
        self.init_ui()
    
    def closeEvent(self, event):
        """Called when the tab/widget is closed - kill all running servers"""
        self.kill_all_servers()
        super().closeEvent(event)
    
    def kill_all_servers(self):
        """Kill all running server processes"""
        for server_path, process in list(self.running_processes.items()):
            if process and process.state() == QProcess.Running:
                process.terminate()
                # Give it a moment to terminate gracefully
                if not process.waitForFinished(2000):
                    process.kill()
                    process.waitForFinished()
        self.running_processes.clear()
    
    def init_ui(self):
        """Initialize the UI with split layout: servers list and terminal"""
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
        
        # Create horizontal layout for servers list and terminal
        content_layout = QHBoxLayout()
        
        # LEFT SIDE: Servers list with label
        left_layout = QVBoxLayout()
        
        servers_label = QLabel("Servers:")
        servers_font = QFont()
        servers_font.setPointSize(12)
        servers_font.setBold(True)
        servers_label.setFont(servers_font)
        left_layout.addWidget(servers_label)
        
        self.servers_list = QListWidget()
        self.servers_list.itemClicked.connect(self.on_server_list_item_clicked)
        self.servers_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(self.servers_list, 1)
        
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
        
        left_layout.addLayout(buttons_layout)
        
        left_frame = QFrame()
        left_frame.setLayout(left_layout)
        left_frame.setMinimumWidth(200)
        content_layout.addWidget(left_frame, 0)
        
        # RIGHT SIDE: Terminal with label
        right_layout = QVBoxLayout()
        
        terminal_label = QLabel("Terminal:")
        terminal_font = QFont()
        terminal_font.setPointSize(12)
        terminal_font.setBold(True)
        terminal_label.setFont(terminal_font)
        right_layout.addWidget(terminal_label)
        
        # Terminal output area
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Courier", 9))
        self.terminal_output.setLineWrapMode(QTextEdit.NoWrap)
        self.terminal_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Connect scrollbar to track user scrolling
        self.terminal_output.verticalScrollBar().valueChanged.connect(self.on_terminal_scroll)
        
        right_layout.addWidget(self.terminal_output, 1)
        
        # Start/Stop buttons
        control_layout = QHBoxLayout()
        
        self.start_server_button = QPushButton("Start Server")
        self.start_server_button.clicked.connect(self.start_server)
        self.start_server_button.setEnabled(False)
        self.start_server_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #27ae60;
            }
            QPushButton:hover:!disabled {
                background-color: #27ae60;
            }
            QPushButton:pressed:!disabled {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        control_layout.addWidget(self.start_server_button)
        
        self.stop_server_button = QPushButton("Stop Server")
        self.stop_server_button.clicked.connect(self.stop_server)
        self.stop_server_button.setEnabled(False)
        self.stop_server_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #c0392b;
            }
            QPushButton:hover:!disabled {
                background-color: #c0392b;
            }
            QPushButton:pressed:!disabled {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        control_layout.addWidget(self.stop_server_button)
        
        right_layout.addLayout(control_layout)
        
        right_frame = QFrame()
        right_frame.setLayout(right_layout)
        right_frame.setMinimumWidth(400)
        content_layout.addWidget(right_frame, 1)
        
        main_layout.addLayout(content_layout, 1)
        
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
        self.current_server_path = server_path
        self.parent_window.server_root = server_path
        self.parent_window.settings.setValue('server_root', server_path)
        
        # Switch to this server's terminal history
        self.update_terminal_display()
        
        # Update button states based on whether THIS server is running
        is_this_server_running = server_path in self.running_processes
        self.start_server_button.setEnabled(not is_this_server_running)
        self.stop_server_button.setEnabled(is_this_server_running)
        
        self.parent_window.auto_load_configs()
        
        # Update virtual steward replay file status
        if self.parent_window.virtual_steward_tab:
            self.parent_window.virtual_steward_tab.on_server_selected()
    
    def update_terminal_display(self):
        """Update the terminal output to show the current server's history"""
        if not self.current_server_path:
            self.terminal_output.clear()
            self.terminal_auto_scroll_enabled = True
            return
        
        # Get or create terminal history for this server
        if self.current_server_path not in self.server_terminals:
            self.server_terminals[self.current_server_path] = QTextEdit()
            self.server_terminals[self.current_server_path].setReadOnly(True)
            self.server_terminals[self.current_server_path].setFont(QFont("Courier", 9))
            self.server_terminals[self.current_server_path].setLineWrapMode(QTextEdit.NoWrap)
        
        # Copy the content from the server's terminal to the display
        terminal_history = self.server_terminals[self.current_server_path]
        self.terminal_output.setPlainText(terminal_history.toPlainText())
        
        # Re-enable auto-scroll when switching servers and scroll to bottom
        self.terminal_auto_scroll_enabled = True
        scrollbar = self.terminal_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def append_terminal_output(self, text: str):
        """Append text to the current server's terminal output"""
        if not self.current_server_path:
            return
        
        # Get or create terminal history for this server
        if self.current_server_path not in self.server_terminals:
            self.server_terminals[self.current_server_path] = QTextEdit()
            self.server_terminals[self.current_server_path].setReadOnly(True)
            self.server_terminals[self.current_server_path].setFont(QFont("Courier", 9))
            self.server_terminals[self.current_server_path].setLineWrapMode(QTextEdit.NoWrap)
        
        # Append to both the history and the display
        self.server_terminals[self.current_server_path].append(text)
        self.terminal_output.append(text)
        
        # Auto-scroll to bottom if enabled
        if self.terminal_auto_scroll_enabled:
            scrollbar = self.terminal_output.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def on_terminal_scroll(self):
        """Detect when user manually scrolls the terminal"""
        scrollbar = self.terminal_output.verticalScrollBar()
        
        # If user scrolled away from bottom, disable auto-scroll
        if scrollbar.value() < scrollbar.maximum():
            self.terminal_auto_scroll_enabled = False
        # If user scrolled back to bottom, re-enable auto-scroll
        elif scrollbar.value() == scrollbar.maximum():
            self.terminal_auto_scroll_enabled = True
    
    def start_server(self):
        """Start the currently selected server"""
        if not self.current_server_path:
            self.append_terminal_output("Error: No server selected")
            return
        
        if self.current_server_path in self.running_processes:
            self.append_terminal_output("Error: This server is already running")
            return
        
        try:
            # Determine the server executable path based on platform
            if sys.platform.startswith('win'):
                server_executable = os.path.join(self.current_server_path, "AssettoServer.exe")
            else:
                server_executable = os.path.join(self.current_server_path, "AssettoServer")
            
            # Check if server executable exists
            if not os.path.exists(server_executable):
                self.append_terminal_output(f"Error: Server executable not found at {server_executable}")
                return
            
            # Create a new QProcess for this server
            process = QProcess(self)
            process.setProgram(server_executable)
            process.setWorkingDirectory(self.current_server_path)
            
            # Store reference to current server path for handlers
            server_path = self.current_server_path
            
            # Connect process signals to slots with server path
            process.readyReadStandardOutput.connect(
                lambda: self.handle_server_output(server_path)
            )
            process.readyReadStandardError.connect(
                lambda: self.handle_server_error(server_path)
            )
            process.finished.connect(
                lambda exit_code, exit_status: self.on_server_finished(server_path, exit_code, exit_status)
            )
            process.errorOccurred.connect(
                lambda error: self.on_server_error(server_path, error)
            )
            
            # Start the server process
            process.start()
            
            if process.waitForStarted():
                # Store the process
                self.running_processes[server_path] = process
                
                self.append_terminal_output(f"\n{'='*60}")
                self.append_terminal_output(f"Starting server from: {server_executable}")
                self.append_terminal_output(f"Working directory: {server_path}")
                self.append_terminal_output(f"Timestamp: {Path(server_path).name}")
                self.append_terminal_output(f"{'='*60}\n")
                
                # Update button states
                self.start_server_button.setEnabled(False)
                self.stop_server_button.setEnabled(True)
                
                # Emit signal that server started
                self.server_started.emit()
            else:
                self.append_terminal_output("Failed to start server process")
                
        except Exception as e:
            self.append_terminal_output(f"Error starting server: {str(e)}")
    
    def stop_server(self):
        """Stop the currently selected server"""
        if not self.current_server_path:
            self.append_terminal_output("Error: No server selected")
            return
        
        if self.current_server_path not in self.running_processes:
            self.append_terminal_output("Error: This server is not running")
            return
        
        process = self.running_processes[self.current_server_path]
        
        if process and process.state() == QProcess.Running:
            self.append_terminal_output("\n" + "="*60)
            self.append_terminal_output("Stopping server...")
            self.append_terminal_output("="*60 + "\n")
            
            process.terminate()
            
            # Give it a moment to terminate gracefully
            if not process.waitForFinished(3000):
                process.kill()
                process.waitForFinished()
                
            self.start_server_button.setEnabled(True)
            self.stop_server_button.setEnabled(False)
            self.append_terminal_output("Server stopped successfully!\n")
            self.server_stopped.emit()
        else:
            self.append_terminal_output("Server process is not running")
    
    def handle_server_output(self, server_path: str):
        """Handle output from the server process"""
        if server_path in self.running_processes:
            process = self.running_processes[server_path]
            output = process.readAllStandardOutput().data().decode('utf-8', errors='replace')
            if output.strip():
                # Only append if we're viewing this server's terminal
                if server_path == self.current_server_path:
                    self.append_terminal_output(output.strip())
                else:
                    # Still add to history, just don't display
                    if server_path not in self.server_terminals:
                        self.server_terminals[server_path] = QTextEdit()
                        self.server_terminals[server_path].setReadOnly(True)
                        self.server_terminals[server_path].setFont(QFont("Courier", 9))
                        self.server_terminals[server_path].setLineWrapMode(QTextEdit.NoWrap)
                    self.server_terminals[server_path].append(output.strip())
    
    def handle_server_error(self, server_path: str):
        """Handle error output from the server process"""
        if server_path in self.running_processes:
            process = self.running_processes[server_path]
            error = process.readAllStandardError().data().decode('utf-8', errors='replace')
            if error.strip():
                # Only append if we're viewing this server's terminal
                if server_path == self.current_server_path:
                    self.append_terminal_output(f"ERROR: {error.strip()}")
                else:
                    # Still add to history
                    if server_path not in self.server_terminals:
                        self.server_terminals[server_path] = QTextEdit()
                        self.server_terminals[server_path].setReadOnly(True)
                        self.server_terminals[server_path].setFont(QFont("Courier", 9))
                        self.server_terminals[server_path].setLineWrapMode(QTextEdit.NoWrap)
                    self.server_terminals[server_path].append(f"ERROR: {error.strip()}")
    
    def on_server_finished(self, server_path: str, exit_code, exit_status):
        """Called when the server process finishes"""
        # Remove from running processes
        if server_path in self.running_processes:
            del self.running_processes[server_path]
        
        # Only update buttons if this is the currently viewed server
        if server_path == self.current_server_path:
            self.start_server_button.setEnabled(True)
            self.stop_server_button.setEnabled(False)
            self.append_terminal_output(f"\nServer process finished with exit code: {exit_code} (Status: {exit_status})")
        else:
            # Add to history if not currently viewed
            if server_path not in self.server_terminals:
                self.server_terminals[server_path] = QTextEdit()
                self.server_terminals[server_path].setReadOnly(True)
                self.server_terminals[server_path].setFont(QFont("Courier", 9))
                self.server_terminals[server_path].setLineWrapMode(QTextEdit.NoWrap)
            self.server_terminals[server_path].append(f"\nServer process finished with exit code: {exit_code} (Status: {exit_status})")
        
        self.server_stopped.emit()
    
    def on_server_error(self, server_path: str, error):
        """Called when an error occurs with the server process"""
        # Remove from running processes
        if server_path in self.running_processes:
            del self.running_processes[server_path]
        
        # Only update buttons if this is the currently viewed server
        if server_path == self.current_server_path:
            self.start_server_button.setEnabled(True)
            self.stop_server_button.setEnabled(False)
            self.append_terminal_output(f"Server process error: {error}")
        else:
            # Add to history if not currently viewed
            if server_path not in self.server_terminals:
                self.server_terminals[server_path] = QTextEdit()
                self.server_terminals[server_path].setReadOnly(True)
                self.server_terminals[server_path].setFont(QFont("Courier", 9))
                self.server_terminals[server_path].setLineWrapMode(QTextEdit.NoWrap)
            self.server_terminals[server_path].append(f"Server process error: {error}")
        
        self.server_stopped.emit()
    
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
