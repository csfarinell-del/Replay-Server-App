"""
Server Terminal Tab for the Assetto Corsa Server Configuration Manager
Displays a tabbed terminal for server output
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QTextEdit, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QProcess, pyqtSignal
from PyQt5.QtGui import QFont

import subprocess
import os
import sys
from pathlib import Path


class ServerTerminalTab(QWidget):
    """Tab for displaying server terminal output in a tabbed interface"""
    
    # Signal to communicate with main window about server status
    server_started = pyqtSignal()
    server_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
        self.setup_terminal_tabs()
        self.process = None  # QProcess for server execution
        self.server_root = None
        self.is_server_running = False
    
    def init_ui(self):
        """Initialize the Server Terminal tab UI"""
        layout = QVBoxLayout()
        
        label = QLabel("Server Terminal")
        label_font = label.font()
        label_font.setPointSize(12)
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        # Create tab widget for terminal output
        self.terminal_tabs = QTabWidget()
        self.terminal_tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.terminal_tabs)
        
        # Add a button to start/stop servers (this would be connected to actual server controls)
        button_layout = QHBoxLayout()
        
        self.start_server_button = QPushButton("Start Server")
        self.start_server_button.clicked.connect(self.start_server)
        button_layout.addWidget(self.start_server_button)
        
        self.stop_server_button = QPushButton("Stop Server")
        self.stop_server_button.setEnabled(False)
        self.stop_server_button.clicked.connect(self.stop_server)
        button_layout.addWidget(self.stop_server_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_terminal_tabs(self):
        """Setup initial terminal tabs"""
        # Create a default tab for server output
        self.default_terminal = QTextEdit()
        self.default_terminal.setReadOnly(True)
        self.default_terminal.setFont(QFont("Courier", 10))
        self.default_terminal.setLineWrapMode(QTextEdit.NoWrap)
        
        # Add to tab widget
        self.terminal_tabs.addTab(self.default_terminal, "Server Output")
    
    def set_server_root(self, server_root_path):
        """Set the server root path for launching the server"""
        self.server_root = server_root_path
    
    def start_server(self):
        """Start the server and display output in terminal using QProcess"""
        # Use the server root from either this tab or parent window
        if not self.server_root:
            if hasattr(self.parent_window, 'server_root') and self.parent_window.server_root:
                self.server_root = self.parent_window.server_root
            else:
                self.default_terminal.append("Error: Server root path not set")
                return

        try:
            # Determine the server executable path based on platform
            if sys.platform.startswith('win'):
                server_executable = os.path.join(self.server_root, "AssettoServer.exe")
            else:
                server_executable = os.path.join(self.server_root, "AssettoServer")
            
            # Check if server executable exists
            if not os.path.exists(server_executable):
                self.default_terminal.append(f"Error: Server executable not found at {server_executable}")
                return

            # Create a new QProcess for the server (this runs within the app)
            self.process = QProcess(self)
            self.process.setProgram(server_executable)
            self.process.setWorkingDirectory(self.server_root)
            
            # Connect process signals to slots
            self.process.readyReadStandardOutput.connect(self.handle_server_output)
            self.process.readyReadStandardError.connect(self.handle_server_error)
            self.process.finished.connect(self.on_server_finished)
            self.process.errorOccurred.connect(self.on_server_error)
            
            # Start the server process (this runs within our application)
            self.process.start()
            
            if self.process.waitForStarted():
                self.default_terminal.append(f"Starting server from: {server_executable}")
                self.default_terminal.append("Server started successfully in application window!")
                self.is_server_running = True
                
                # Update button states
                self.start_server_button.setEnabled(False)
                self.stop_server_button.setEnabled(True)
                
                # Emit signal that server started
                self.server_started.emit()
            else:
                self.default_terminal.append("Failed to start server process")
                self.process = None
                
        except Exception as e:
            self.default_terminal.append(f"Error starting server: {str(e)}")
    
    def stop_server(self):
        """Stop the server gracefully"""
        if self.is_server_running and self.process and self.process.state() == QProcess.Running:
            self.default_terminal.append("Stopping server...")
            self.process.terminate()
            
            # Give it a moment to terminate gracefully
            if not self.process.waitForFinished(3000):
                self.process.kill()
                self.process.waitForFinished()
                
            self.is_server_running = False
            self.start_server_button.setEnabled(True)
            self.stop_server_button.setEnabled(False)
            self.default_terminal.append("Server stopped successfully!")
            self.server_stopped.emit()
        else:
            self.default_terminal.append("No server is currently running")
    
    def handle_server_output(self):
        """Handle output from the server process"""
        output = self.process.readAllStandardOutput().data().decode('utf-8')
        if output.strip():
            self.default_terminal.append(output.strip())
    
    def handle_server_error(self):
        """Handle error output from the server process"""
        error = self.process.readAllStandardError().data().decode('utf-8')
        if error.strip():
            self.default_terminal.append(f"ERROR: {error.strip()}")
    
    def on_server_finished(self, exit_code, exit_status):
        """Called when the server process finishes"""
        self.is_server_running = False
        self.start_server_button.setEnabled(True)
        self.stop_server_button.setEnabled(False)
        self.default_terminal.append(f"Server process finished with exit code: {exit_code} (Status: {exit_status})")
        self.server_stopped.emit()
    
    def on_server_error(self, error):
        """Called when an error occurs with the server process"""
        self.is_server_running = False
        self.start_server_button.setEnabled(True)
        self.stop_server_button.setEnabled(False)
        self.default_terminal.append(f"Server process error: {error}")
        self.server_stopped.emit()
    
    def add_server_tab(self, server_name):
        """Add a new tab for a specific server instance"""
        terminal = QTextEdit()
        terminal.setReadOnly(True)
        terminal.setFont(QFont("Courier", 10))
        terminal.setLineWrapMode(QTextEdit.NoWrap)
        
        self.terminal_tabs.addTab(terminal, server_name)
        self.terminal_tabs.setCurrentWidget(terminal)
    
    def update_terminal_output(self, output_text):
        """Update the terminal with new output text"""
        if hasattr(self, 'default_terminal') and self.default_terminal:
            self.default_terminal.append(output_text)