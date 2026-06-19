"""
Custom dialog windows for the Assetto Corsa Server Configuration Manager

This module provides reusable selection dialogs for cars, tracks, and skins.
Each dialog features a search box for quick filtering through large lists.

Search Persistence:
- Each dialog class uses a class-level variable (_last_search_text) to persist search terms
- When a dialog is closed and reopened, the previous search term appears automatically
- This provides continuity when users repeatedly search for the same items
- Search state is shared across all instances of a dialog class during the session

Dialog Patterns:
- All dialogs inherit from QDialog and follow a consistent layout
- Table displays all available items (sorted alphabetically)
- Search input filters the table in real-time
- OK/Cancel buttons for user confirmation
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QLineEdit, QPushButton, QLabel
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class CarSelectionDialog(QDialog):
    """Dialog for selecting a car with search functionality"""
    
    # Class variable to persist search across instances (intentional sharing)
    _last_search_text = ""
    
    def __init__(self, available_cars, parent=None):
        super().__init__(parent)
        self.available_cars = available_cars
        self.selected_car = None
        
        self.setWindowTitle("Select Car")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.setText(self._last_search_text)
        self.search_input.textChanged.connect(self.filter_cars)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Car list table
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Car"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self.on_car_double_clicked)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.select_car)
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Populate table
        self.populate_cars()
        self.search_input.setFocus()
    
    def populate_cars(self):
        """Populate car list table"""
        self.table.setRowCount(len(self.available_cars))
        
        for row, car in enumerate(sorted(self.available_cars.values())):
            item = QTableWidgetItem(car)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item)
    
    def filter_cars(self, text):
        """Filter cars based on search text"""
        self._last_search_text = text
        search_lower = text.lower()
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                visible = search_lower in item.text().lower()
                self.table.setRowHidden(row, not visible)
    
    def on_car_double_clicked(self, index):
        """Select car on double-click"""
        self.select_car()
    
    def select_car(self):
        """Get selected car"""
        selected = self.table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            item = self.table.item(row, 0)
            if item:
                display_name = item.text()
                # Find original name from display name
                for orig, display in self.available_cars.items():
                    if display == display_name:
                        self.selected_car = orig
                        break
                self.accept()
    
    def closeEvent(self, event):
        """Save search text when closing"""
        self._last_search_text = self.search_input.text()
        super().closeEvent(event)


class SkinSelectionDialog(QDialog):
    """Dialog for selecting a car skin with preview images"""
    
    def __init__(self, available_skins, content_root, car_model, parent=None):
        super().__init__(parent)
        self.available_skins = available_skins
        self.content_root = content_root
        self.car_model = car_model
        self.selected_skin = None
        
        self.setWindowTitle(f"Select Skin for {car_model}")
        self.setGeometry(100, 100, 400, 500)
        
        layout = QVBoxLayout()
        
        # Skin list table with preview
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Skin", "Preview"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 200)
        self.table.setRowHeight(0, 80)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self.on_skin_double_clicked)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.select_skin)
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Populate table
        self.populate_skins()
    
    def populate_skins(self):
        """Populate skin list with preview images"""
        self.table.setRowCount(len(self.available_skins))
        
        for row, skin in enumerate(sorted(self.available_skins)):
            # Skin name
            skin_item = QTableWidgetItem(skin)
            skin_item.setFlags(skin_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, skin_item)
            
            # Preview image
            preview_path = Path(self.content_root) / "cars" / self.car_model / "skins" / skin / "preview.jpg"
            if preview_path.exists():
                pixmap = QPixmap(str(preview_path))
                if not pixmap.isNull():
                    scaled = pixmap.scaledToHeight(75, Qt.SmoothTransformation)
                    preview_item = QTableWidgetItem()
                    preview_item.setData(Qt.DecorationRole, scaled)
                    preview_item.setFlags(preview_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, 1, preview_item)
            
            self.table.setRowHeight(row, 80)
    
    def on_skin_double_clicked(self, index):
        """Select skin on double-click"""
        self.select_skin()
    
    def select_skin(self):
        """Get selected skin"""
        selected = self.table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            item = self.table.item(row, 0)
            if item:
                self.selected_skin = item.text()
                self.accept()


class TrackSelectionDialog(QDialog):
    """Dialog for selecting a track with search functionality"""
    
    _last_search_text = ""  # Class variable to persist search
    
    def __init__(self, available_tracks, parent=None):
        super().__init__(parent)
        self.available_tracks = available_tracks
        self.selected_track = None
        
        self.setWindowTitle("Select Track")
        self.setGeometry(100, 100, 400, 400)
        
        layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.setText(self._last_search_text)
        self.search_input.textChanged.connect(self.filter_tracks)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Track list table
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Track"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self.on_track_double_clicked)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.select_track)
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Populate table
        self.populate_tracks()
        self.search_input.setFocus()
    
    def populate_tracks(self):
        """Populate track list table"""
        self.table.setRowCount(len(self.available_tracks))
        
        for row, track in enumerate(sorted(self.available_tracks)):
            item = QTableWidgetItem(track)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item)
    
    def filter_tracks(self, text):
        """Filter tracks based on search text"""
        self._last_search_text = text
        search_lower = text.lower()
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                visible = search_lower in item.text().lower()
                self.table.setRowHidden(row, not visible)
    
    def on_track_double_clicked(self, index):
        """Select track on double-click"""
        self.select_track()
    
    def select_track(self):
        """Get selected track"""
        selected = self.table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            item = self.table.item(row, 0)
            if item:
                self.selected_track = item.text()
                self.accept()
    
    def closeEvent(self, event):
        """Save search text when closing"""
        self._last_search_text = self.search_input.text()
        super().closeEvent(event)
