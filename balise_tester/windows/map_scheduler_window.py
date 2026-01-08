"""Window for editing train schedules."""

import copy
import csv
import datetime
import os
from typing import Optional

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QColor, QBrush, QKeySequence
from PySide6.QtWidgets import (QFileDialog, QHeaderView, QInputDialog,
                               QMainWindow, QMenu, QMessageBox, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from ui.map import Ui_Map_MainWindow
from .map_preview_dialog import MapPreviewDialog


class MapSchedulerWindow(QMainWindow, Ui_Map_MainWindow):
    """Train schedule editor window.

    Manages editing, importing, exporting, and versioning (undo/redo) of
    train schedules.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the map scheduler window."""
        super().__init__(parent)
        self.setupUi(self)
        
        # Initialize Data Table
        self.init_table()
        
        # Undo/Redo Stacks
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 50
        
        # Current File
        self.current_file_path = None
        
        # Connect Menus
        self.init_menus()
        
        # Connect to Simulation Time if parent has it
        if parent and hasattr(parent, 'simulation_widget'):
            parent.simulation_widget.sim_time_updated.connect(self.update_highlight)
        
        # Initial State
        self.save_state_to_history()

        # Load last file
        self.load_last_file()

    def init_table(self):
        """初始化表格控件"""
        self.layout = QVBoxLayout(self.centralwidget)
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)
        
        # Columns: "列车、起始站、到起始站时间、发车时间、到达站、出到达站时间、到达时间"
        self.headers = ["列车", "起始站", "到起始站时间", "发车时间", "到达站", "出到达站时间", "到达时间"]
        self.table_widget.setColumnCount(len(self.headers))
        self.table_widget.setHorizontalHeaderLabels(self.headers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Connect change signal for undo/redo (debouncing might be needed for text changes, 
        # but for cell changed it's okay)
        self.table_widget.itemChanged.connect(self.on_item_changed)
        
        # Track programmatic changes to avoid loop
        self.is_programmatic_change = False

        # Cache last highlighted rows to avoid repainting entire table each tick
        self.last_current_row = -1
        self.last_next_row = -1

    def init_menus(self):
        """初始化菜单行为"""
        # --- File / New ---
        self.action_new = QAction("新建", self)
        self.action_new.setShortcut(QKeySequence.New)
        self.action_new.triggered.connect(self.new_file)
        self.menu_new.addAction(self.action_new) # Assuming menu_new is QMenu
        
        # --- File / Import (Open) ---
        self.action_import = QAction("导入...", self)
        self.action_import.setShortcut(QKeySequence.Open)
        self.action_import.triggered.connect(self.import_file)
        self.menu_import.addAction(self.action_import)
        
        # --- File / Save ---
        self.action_save = QAction("保存", self)
        self.action_save.setShortcut(QKeySequence.Save)
        self.action_save.triggered.connect(self.save_file)
        
        self.action_save_as = QAction("另存为...", self)
        self.action_save_as.setShortcut(QKeySequence.SaveAs)
        self.action_save_as.triggered.connect(self.save_as_file)
        
        self.menu_save.addAction(self.action_save)
        self.menu_save.addAction(self.action_save_as)
        
        # --- Edit ---
        # "Edit" menu usually contains operations.
        self.action_add_row = QAction("添加行", self)
        self.action_add_row.triggered.connect(self.add_row)
        self.menu_edit.addAction(self.action_add_row)
        
        self.action_del_row = QAction("删除行", self)
        self.action_del_row.setShortcut(QKeySequence.Delete)
        self.action_del_row.triggered.connect(self.delete_row)
        self.menu_edit.addAction(self.action_del_row)
        
        # --- Undo / Redo ---
        self.action_undo = QAction("撤销", self)
        self.action_undo.setShortcut(QKeySequence.Undo)
        self.action_undo.triggered.connect(self.undo)
        self.menu_undo.addAction(self.action_undo)
        
        self.action_redo = QAction("重做", self)
        self.action_redo.setShortcut(QKeySequence.Redo)
        self.action_redo.triggered.connect(self.redo)
        self.menu_redo.addAction(self.action_redo)

        # --- Preview ---
        self.action_preview = QAction("预览运行图", self)
        self.action_preview.triggered.connect(self.show_preview)
        # Add to Menu (if menu_view exists, or just toolbar/edit)
        # Assuming no dedicated View menu in ui file, add to Edit or create new?
        # Let's add to Edit for now or create a toolbar later.
        # Check UI file again... menu_edit, menu_undo, etc.
        # Maybe add to menu_edit?
        self.menu_edit.addSeparator()
        self.menu_edit.addAction(self.action_preview)

    # --- Logic ---
    
    def show_preview(self):
        """显示运行图预览"""
        data = self.get_table_data()
        
        # We need stations list. Try to get from parent main window
        stations = []
        line_length = 100.0
        parent = self.parent()
        if parent and hasattr(parent, 'stations'):
            stations = parent.stations
        if parent and hasattr(parent, 'get_max_length'):
            line_length = parent.get_max_length()
            
        dialog = MapPreviewDialog(self, schedule_data=data, stations=stations, line_length=line_length)
        dialog.exec()

    def get_table_data(self):
        """Get current table data as list of lists"""
        rows = self.table_widget.rowCount()
        cols = self.table_widget.columnCount()
        data = []
        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = self.table_widget.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def set_table_data(self, data):
        """Set table data from list of lists"""
        self.is_programmatic_change = True
        self.table_widget.setRowCount(0)
        self.table_widget.setRowCount(len(data))
        for r, row_data in enumerate(data):
            for c, text in enumerate(row_data):
                if c < self.table_widget.columnCount():
                    self.table_widget.setItem(r, c, QTableWidgetItem(str(text)))
        self.is_programmatic_change = False

    def save_state_to_history(self):
        """Save current state to undo stack"""
        if self.is_programmatic_change:
            return
            
        current_state = self.get_table_data()
        
        # Avoid duplicate states if nothing changed (optional)
        if self.undo_stack and self.undo_stack[-1] == current_state:
            return

        self.undo_stack.append(current_state)
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
            
        # Clear redo stack on new change
        self.redo_stack.clear()

    def on_item_changed(self, item):
        self.save_state_to_history()

    def load_last_file(self):
        """加载最近编辑的文件"""
        settings = QSettings("BaliseTester", "MapScheduler")
        last_path = settings.value("last_file_path", "")
        if last_path and os.path.exists(last_path):
            try:
                self.load_csv(last_path)
                print(f"Loaded recent file: {last_path}")
            except Exception as e:
                print(f"Failed to load recent file: {e}")

    def save_last_path(self, path):
        """保存最近编辑的文件路径"""
        settings = QSettings("BaliseTester", "MapScheduler")
        settings.setValue("last_file_path", path)

    def load_csv(self, path):
        """读取CSV并填充表格"""
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None) # Skip header
            data = list(reader)
            
        self.set_table_data(data)
        self.current_file_path = path
        self.save_state_to_history()
        self.save_last_path(path)

    # --- Actions ---

    def _get_map_data_dir(self):
        """Get the absolute path to the data/map directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # balise_tester/windows/map_scheduler_window.py -> .../Balise_Tester
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        return os.path.join(project_root, "data", "map")

    def new_file(self):
        if self.table_widget.rowCount() > 0:
            res = QMessageBox.question(self, "确认", "新建将清空当前表格，是否继续？", 
                                       QMessageBox.Yes | QMessageBox.No)
            if res != QMessageBox.Yes:
                return
        
        self.is_programmatic_change = True
        self.table_widget.setRowCount(0)
        self.current_file_path = None
        self.is_programmatic_change = False
        self.save_state_to_history()

    def import_file(self):
        default_dir = self._get_map_data_dir()
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)
            
        path, _ = QFileDialog.getOpenFileName(self, "导入CSV", default_dir, "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
            
        try:
            self.load_csv(path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

    def save_file(self):
        if not self.current_file_path:
            self.save_as_file()
        else:
            self._write_csv(self.current_file_path)

    def save_as_file(self):
        default_dir = self._get_map_data_dir()
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)
            
        path, _ = QFileDialog.getSaveFileName(self, "保存CSV", default_dir, "CSV Files (*.csv)")
        if path:
            self._write_csv(path)

    def _write_csv(self, path):
        try:
            data = self.get_table_data()
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                writer.writerows(data)
            self.current_file_path = path
            self.save_last_path(path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def add_row(self):
        self.is_programmatic_change = True
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)
        self.is_programmatic_change = False
        self.save_state_to_history()

    def delete_row(self):
        """Delete selected rows or current row."""
        # Get all selected rows
        selected_rows = set()
        for idx in self.table_widget.selectedIndexes():
            selected_rows.add(idx.row())
            
        # Fallback to current row if no selection but there is a current item
        if not selected_rows:
            curr = self.table_widget.currentRow()
            if curr >= 0:
                selected_rows.add(curr)
                
        if not selected_rows:
            return

        self.is_programmatic_change = True
        # Sort in reverse order to keep indices valid while removing
        for row in sorted(selected_rows, reverse=True):
            self.table_widget.removeRow(row)
        self.is_programmatic_change = False
        self.save_state_to_history()

    def undo(self):
        if len(self.undo_stack) <= 1:
            return
            
        # Current state is top of undo stack
        current = self.undo_stack.pop()
        self.redo_stack.append(current)
        
        # Previous state
        prev = self.undo_stack[-1]
        self.set_table_data(prev)

    def redo(self):
        if not self.redo_stack:
            return
            
        next_state = self.redo_stack.pop()
        self.undo_stack.append(next_state)
        self.set_table_data(next_state)

    def _parse_time(self, time_str):
        if not time_str or not isinstance(time_str, str): 
            return None
        time_str = time_str.strip()
        if not time_str: return None
        
        # Use simple today date
        today = datetime.date.today()
        
        for fmt in ["%H:%M:%S", "%H:%M"]:
            try:
                t = datetime.datetime.strptime(time_str, fmt).time()
                return datetime.datetime.combine(today, t)
            except ValueError:
                continue
        return None

    def _apply_row_style(self, row, bg_color=None, fg_color=None):
        """Apply background/foreground to a single row only (lightweight)."""
        cols = self.table_widget.columnCount()
        for c in range(cols):
            item = self.table_widget.item(row, c)
            if not item:
                continue
            if bg_color is None:
                item.setData(Qt.BackgroundRole, None)
            else:
                item.setBackground(QBrush(bg_color))
            if fg_color is None:
                item.setForeground(QBrush(Qt.white))
            else:
                item.setForeground(QBrush(fg_color))

    def update_highlight(self, current_dt):
        """Highlight current train (Green) and next train (Yellow)."""
        if not current_dt or self.table_widget.rowCount() == 0:
            return
            
        # Current time normalized to today for comparison (ignoring date shift for daily schedule)
        now_time = current_dt.time()
        now = datetime.datetime.combine(datetime.date.today(), now_time)
        
        rows = self.table_widget.rowCount()
        next_train_row = -1
        min_diff = float('inf')
        current_row = -1
        
        # Color constants
        COLOR_CURRENT = QColor("#90EE90") # Light Green
        COLOR_NEXT = QColor("#FFFFE0")    # Light Yellow

        # Single pass: determine current and next rows without painting
        for r in range(rows):
            item_dep = self.table_widget.item(r, 3)
            item_arr = self.table_widget.item(r, 6)
            
            t_dep = self._parse_time(item_dep.text()) if item_dep else None
            t_arr = self._parse_time(item_arr.text()) if item_arr else None
            
            if not (t_dep and t_arr):
                continue

            actual_arr = t_arr + datetime.timedelta(days=1) if t_arr < t_dep else t_arr
            
            if current_row == -1 and t_dep <= now <= actual_arr:
                current_row = r
                # Do not break; we still want to find the next upcoming train
                continue

            if t_dep > now:
                diff = (t_dep - now).total_seconds()
                if diff < min_diff:
                    min_diff = diff
                    next_train_row = r

        # If nothing changed, skip repaint
        if current_row == self.last_current_row and next_train_row == self.last_next_row:
            return

        # Clear old highlights (only the rows we touched previously)
        for old_row in {self.last_current_row, self.last_next_row}:
            if old_row != -1 and old_row not in (current_row, next_train_row):
                self._apply_row_style(old_row, None, None)

        # Apply new highlights
        if current_row != -1:
            self._apply_row_style(current_row, COLOR_CURRENT, Qt.black)
        if next_train_row != -1 and next_train_row != current_row:
            self._apply_row_style(next_train_row, COLOR_NEXT, Qt.black)

        # Update cache
        self.last_current_row = current_row
        self.last_next_row = next_train_row
