"""
Custom PyQt5 Widgets for the Assetto Corsa Server Configuration Manager
"""

from PyQt5.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem, QAbstractItemView, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint, QRect


class PathLineEdit(QLineEdit):
    """
    A QLineEdit that emits a signal when focus is lost.
    Used for path inputs to trigger content discovery.
    """
    focusLost = pyqtSignal()
    
    def focusOutEvent(self, event):
        """Emit focusLost signal when focus is lost"""
        self.focusLost.emit()
        super().focusOutEvent(event)


class ClickableLineEdit(QLineEdit):
    """
    A QLineEdit that emits a signal on double-click.
    Used for opening file dialogs on double-click.
    """
    doubleClicked = pyqtSignal()
    
    def mouseDoubleClickEvent(self, event):
        """Emit doubleClicked signal on double-click"""
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class EntryListTable(QTableWidget):
    """
    A custom QTableWidget with drag-and-drop row reordering.
    Emits rowDropped signal when rows are reordered.
    """
    rowDropped = pyqtSignal(int, int)  # (source_row, dest_row)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Auto-scroll timer
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self._on_scroll_timer)
        self.scroll_speed = 0
        
        # Track drag operation
        self.drag_start_row = None
    
    def dragEnterEvent(self, event):
        """Accept drag events"""
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag movement - auto-scroll near edges"""
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            # Auto-scroll when dragging near top or bottom
            pos = event.pos()
            margin = 50
            
            if pos.y() < margin:
                # Near top - scroll up
                self.scroll_speed = -5
                self.scroll_timer.start(20)
            elif pos.y() > self.height() - margin:
                # Near bottom - scroll down
                self.scroll_speed = 5
                self.scroll_timer.start(20)
            else:
                # In middle - stop scrolling
                self.scroll_timer.stop()
                self.scroll_speed = 0
            
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Stop auto-scroll when dragging leaves"""
        self.scroll_timer.stop()
        self.scroll_speed = 0
        event.accept()
    
    def dropEvent(self, event):
        """Handle drop event - emit custom signal instead of internal reorder"""
        if not event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.ignore()
            return
        
        self.scroll_timer.stop()
        self.scroll_speed = 0
        
        # Get source and destination rows
        source_index = self.indexAt(event.pos())
        if not source_index.isValid():
            event.ignore()
            return
        
        dest_row = source_index.row()
        
        # Get source row from selected rows
        selected = self.selectionModel().selectedRows()
        if not selected:
            event.ignore()
            return
        
        src_row = selected[0].row()
        
        # Emit custom signal instead of doing internal reorder
        if src_row != dest_row:
            self.rowDropped.emit(src_row, dest_row)
        
        event.setDropAction(Qt.DropAction.MoveAction)
        event.accept()
    
    def _on_scroll_timer(self):
        """Auto-scroll timer callback"""
        if self.scroll_speed != 0:
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + self.scroll_speed
            )
