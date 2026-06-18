"""
Virtual Steward Tab for the Assetto Corsa Server Configuration Manager
Handles Virtual Steward plugin configuration
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox,
    QSlider, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

import file_manager


class VirtualStewardTab(QWidget):
    """Virtual Steward tab for plugin configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # UI elements
        self.vs_enabled_checkbox = None
        self.add_replay_btn = None
        self.loop_lap_input = None
        self.bot_trains_checkbox = None
        self.train_gap_slider = None
        self.train_gap_value_label = None
        self.num_bots_combo = None
        self.replay_file_warning = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout()
        
        # Virtual Steward Configuration title
        from PyQt5.QtGui import QFont
        vs_title = QLabel("Virtual Steward Configuration")
        vs_font = QFont()
        vs_font.setPointSize(12)
        vs_font.setBold(True)
        vs_title.setFont(vs_font)
        main_layout.addWidget(vs_title)
        
        # Virtual Steward Enable checkbox
        self.vs_enabled_checkbox = QCheckBox("Enable Virtual Steward Replay Plugin")
        self.vs_enabled_checkbox.stateChanged.connect(self.on_vs_enabled_changed)
        main_layout.addWidget(self.vs_enabled_checkbox)
        
        # Replay file section
        replay_layout = QHBoxLayout()
        replay_layout.addWidget(QLabel("Replay File:"))
        self.add_replay_btn = QPushButton("Select Replay File...")
        self.add_replay_btn.clicked.connect(self.on_add_replay_file_clicked)
        self.add_replay_btn.setEnabled(False)
        replay_layout.addWidget(self.add_replay_btn)
        replay_layout.addStretch()
        main_layout.addLayout(replay_layout)
        
        # Replay warning label
        self.replay_file_warning = QLabel("⚠ No replay file found!")
        self.replay_file_warning.setStyleSheet("color: orange;")
        self.replay_file_warning.setVisible(False)
        main_layout.addWidget(self.replay_file_warning)
        
        # Loop lap section
        lap_layout = QHBoxLayout()
        self.lap_label = QLabel("Loop Lap:")
        self.loop_lap_input = QLineEdit()
        self.loop_lap_input.setPlaceholderText("Leave empty to loop entire race")
        self.loop_lap_input.setEnabled(False)
        lap_layout.addWidget(self.lap_label)
        lap_layout.addWidget(self.loop_lap_input)
        lap_layout.addStretch()
        main_layout.addLayout(lap_layout)
        
        # Bot trains section
        bot_trains_layout = QHBoxLayout()
        self.bot_trains_checkbox = QCheckBox("Enable Bot Trains")
        self.bot_trains_checkbox.setEnabled(False)
        bot_trains_layout.addWidget(self.bot_trains_checkbox)
        bot_trains_layout.addStretch()
        main_layout.addLayout(bot_trains_layout)
        
        # Gap slider section
        gap_layout = QHBoxLayout()
        self.gap_label = QLabel("Train Gap (meters):")
        gap_layout.addWidget(self.gap_label)
        
        self.train_gap_slider = QSlider(Qt.Horizontal)
        self.train_gap_slider.setMinimum(5)
        self.train_gap_slider.setMaximum(100)
        self.train_gap_slider.setValue(5)
        self.train_gap_slider.setEnabled(False)
        self.train_gap_slider.valueChanged.connect(self.on_gap_slider_changed)
        gap_layout.addWidget(self.train_gap_slider)
        
        self.train_gap_value_label = QLabel("5")
        self.train_gap_value_label.setMaximumWidth(30)
        gap_layout.addWidget(self.train_gap_value_label)
        
        main_layout.addLayout(gap_layout)
        
        # Number of bots section
        from PyQt5.QtWidgets import QComboBox
        
        num_bots_layout = QHBoxLayout()
        self.num_bots_label = QLabel("Number of Bots:")
        num_bots_layout.addWidget(self.num_bots_label)
        
        self.num_bots_combo = QComboBox()
        self.num_bots_combo.setEnabled(False)
        self.num_bots_combo.currentIndexChanged.connect(self.parent_window.on_num_bots_changed)
        num_bots_layout.addWidget(self.num_bots_combo)
        
        num_bots_layout.addStretch()
        main_layout.addLayout(num_bots_layout)
        
        # Add spacer
        main_layout.addStretch()
        
        # Links section
        links_layout = QHBoxLayout()
        patreon_link = QLabel('<a href="https://www.patreon.com/admins">Support on Patreon</a>')
        patreon_link.setOpenExternalLinks(True)
        links_layout.addWidget(patreon_link)
        links_layout.addStretch()
        main_layout.addLayout(links_layout)
        
        self.setLayout(main_layout)
    
    def on_vs_enabled_changed(self):
        """Handle Virtual Steward enable/disable"""
        is_checked = self.vs_enabled_checkbox.isChecked()
        
        # Enable/disable controls
        self.add_replay_btn.setEnabled(is_checked)
        self.loop_lap_input.setEnabled(is_checked)
        self.bot_trains_checkbox.setEnabled(is_checked)
        self.train_gap_slider.setEnabled(is_checked and self.bot_trains_checkbox.isChecked())
        self.train_gap_value_label.setEnabled(is_checked and self.bot_trains_checkbox.isChecked())
        self.num_bots_combo.setEnabled(is_checked)
        
        # Update bot config on state change
        self.parent_window.on_vs_enabled_changed()
        self.parent_window.on_num_bots_changed()
        self.parent_window.mark_as_modified()
    
    def on_add_replay_file_clicked(self):
        """Handle replay file selection"""
        if not self.parent_window.server_root:
            QMessageBox.warning(self, "Error", "Please select a server first")
            return
        
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Replay File",
            "",
            "Replay Files (*.acreplay);;All Files (*)"
        )
        
        if file_path:
            try:
                # Copy replay file to server root
                dest_path = Path(self.parent_window.server_root) / "replay.acreplay"
                
                import shutil
                shutil.copy(file_path, str(dest_path))
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Replay file copied to server:\n{dest_path}"
                )
                
                self.parent_window.on_vs_enabled_changed()
                self.parent_window.mark_as_modified()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy replay file: {str(e)}")
    
    def on_gap_slider_changed(self):
        """Handle gap slider value change"""
        value = self.train_gap_slider.value()
        self.train_gap_value_label.setText(str(value))
        
        if self.bot_trains_checkbox.isChecked():
            self.parent_window.mark_as_modified()
