"""Main window module for the Balise Tester application."""

import csv
import os
from functools import partial

from PySide6.QtCore import QFileSystemWatcher, Qt, QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenu

from ui.main import Ui_MainWindow
from .core.config_manager import ConfigManager
from .dialogs.balise_dialog import BaliseConfigDialog
from .dialogs.line_dialog import LineConfigDialog
from .dialogs.station_dialog import StationConfigDialog
from .dialogs.train_dialog import TrainConfigDialog
from .widgets.simulation_widget import SimulationWidget
from .windows.about_window import AboutWindow
from .windows.map_preview_dialog import MapPreviewDialog
from .windows.map_scheduler_window import MapSchedulerWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main window class.

    Responsible for initializing the application interface, managing configuration
    data (balises, stations, trains, lines), handling user interactions, and
    interacting with the simulation widget.
    """

    def __init__(self):
        """
        初始化主窗口。
        设置UI，加载配置，初始化文件监控，连接信号与槽，并初始化菜单。
        """
        super().__init__()
        self.setupUi(self)

        self.config_manager = ConfigManager()
        self.balises = self.config_manager.load_balises()
        self.stations = self.config_manager.load_stations()
        self.trains = self.config_manager.load_trains()
        self.line_config = self.config_manager.load_line_config()

        # Setup File Watcher
        self.file_watcher = QFileSystemWatcher(self)
        if os.path.exists(self.config_manager.balise_csv_file):
            self.file_watcher.addPath(self.config_manager.balise_csv_file)
        self.file_watcher.fileChanged.connect(self.on_balise_file_changed)

        # Setup Simulation Widget
        self.simulation_widget = SimulationWidget(self.run_widget)
        self.simulation_widget.setGeometry(self.run_widget.rect())
        self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config)

        # Connect Actions
        self.action_balise_create.triggered.connect(self.create_balise)
        self.action_station_create.triggered.connect(self.create_station)
        self.action_train_create.triggered.connect(self.create_train)
        self.actionline_maxlength.triggered.connect(self.edit_line_config)
        self.actionmap_draw.triggered.connect(self.open_map_scheduler)

        self.action_run.triggered.connect(self.start_simulation)
        self.action_stop.triggered.connect(self.stop_simulation)
        self.action_pause.triggered.connect(self.pause_simulation)

        self.action_config_save.triggered.connect(self.save_all_config)

        self.actionabout.triggered.connect(self.show_about_dialog)

        # Map preview action from UI
        if hasattr(self, 'actionmap_view'):
            self.actionmap_view.triggered.connect(self.open_map_preview)

        # Connect View Actions
        self.actionzoom_in.triggered.connect(self.simulation_widget.zoom_in)
        self.actionzoom_out.triggered.connect(self.simulation_widget.zoom_out)
        self.actionreload_size.triggered.connect(self.simulation_widget.auto_fit_view)
        self.actionfollow.triggered.connect(self.enable_follow_mode)

        # Connect Simulation Signals
        self.simulation_widget.trains_updated.connect(self.update_train_info)
        self.simulation_widget.sim_time_updated.connect(self.update_sim_time_label)
        self.simulation_widget.balise_create_requested.connect(self.create_balise)
        self.simulation_widget.balise_edit_requested.connect(self.edit_balise)
        self.simulation_widget.balise_moved.connect(self.update_balise_location)

        # Initialize Menus
        self.update_menus()

        # Initial update of train info
        self.update_train_info(self.trains)

        # Instance for About Window
        self.about_window = None

        # Start simulation automatically if schedule is loaded
        if self.simulation_widget.schedule_entries:
            self.start_simulation()
        else:
            self.statuslabel.setText("Status: STOP")

    def update_balise_location(self, index, new_location):
        """Update balise location after drag operation in simulation widget."""
        if 0 <= index < len(self.balises):
            self.balises[index]["location"] = new_location
            # We don't save to file automatically to avoid slowdowns during drag,
            # but updating the memory model ensures subsequent 'Save Config' 
            # or 'Edit' actions use the correct position.
            print(f"Balise {index} moved to {new_location}")

    def on_balise_file_changed(self, path):
        """
        处理应答器配置文件（CSV）变化事件。
        当文件被外部程序修改时，自动重新加载配置并刷新界面。
        
        Args:
            path (str): 发生变化的文件路径。
        """
        # Handle atomic saves (file might be briefly missing)
        if not os.path.exists(path):
            return

        try:
            # Reload balises
            new_balises = self.config_manager.load_balises()
            self.balises = new_balises

            # Update simulation widget
            self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                              reset_view=False, preserve_state=True)

            # Update menus
            self.update_menus()

            # Re-add path to watcher if it was dropped (common with some editors)
            if path not in self.file_watcher.files():
                self.file_watcher.addPath(path)

            print(f"Config reloaded from {path}")
        except Exception as e:
            print(f"Error reloading config: {e}")

    def enable_follow_mode(self):
        """
        启用列车跟随模式。
        视图将自动跟随第一列移动的列车。
        """
        self.simulation_widget.set_follow_mode(True)

    def resizeEvent(self, event):
        """
        处理窗口大小调整事件。
        保持仿真控件与主窗口布局的一致性。
        
        Args:
            event (QResizeEvent): 大小调整事件对象。
        """
        self.simulation_widget.setGeometry(self.run_widget.rect())
        super().resizeEvent(event)

    def get_max_length(self):
        """
        获取线路总长度配置。
        
        Returns:
            float: 线路总长度（km）。默认100.0。
        """
        return self.line_config.get("total_length", 100.0)

    def update_menus(self):
        """
        更新菜单栏内容。
        根据当前的应答器、车站和列车列表，动态生成对应的配置、删除和定位菜单项。
        """
        # Clear existing menus
        self.menu_balise_list.clear()
        self.menu_station_list.clear()
        self.menu_train_list.clear()

        # Populate Balise Menu
        for i, balise in enumerate(self.balises):
            name = balise.get("name", f"Balise {i}")
            menu = QMenu(name, self.menu_balise_list)
            self.menu_balise_list.addMenu(menu)

            action_config = QAction("配置", self)
            action_config.triggered.connect(partial(self.edit_balise, i))
            menu.addAction(action_config)

            action_del = QAction("删除", self)
            action_del.triggered.connect(partial(self.delete_balise, i))
            menu.addAction(action_del)

            action_locate = QAction("定位", self)
            action_locate.triggered.connect(partial(self.locate_balise, i))
            menu.addAction(action_locate)

        # Populate Station Menu
        for i, station in enumerate(self.stations):
            name = station.get("name", f"Station {i}")
            menu = QMenu(name, self.menu_station_list)
            self.menu_station_list.addMenu(menu)

            action_config = QAction("配置", self)
            action_config.triggered.connect(partial(self.edit_station, i))
            menu.addAction(action_config)

            action_del = QAction("删除", self)
            action_del.triggered.connect(partial(self.delete_station, i))
            menu.addAction(action_del)

        # Populate Train Menu
        for i, train in enumerate(self.trains):
            name = train.get("name", f"Train {i}")
            menu = QMenu(name, self.menu_train_list)
            self.menu_train_list.addMenu(menu)

            action_config = QAction("配置", self)
            action_config.triggered.connect(partial(self.edit_train, i))
            menu.addAction(action_config)

            action_del = QAction("删除", self)
            action_del.triggered.connect(partial(self.delete_train, i))
            menu.addAction(action_del)

    def create_balise(self, location=None):
        """
        创建新的应答器。
        打开配置对话框，确认后保存并更新显示。
        
        Args:
            location (float, optional): 如果指定，作为新应答器的初始公里标位置。
        """
        initial_data = {}
        # If called from signal, location is float. If from action, it's bool (False) or None
        if isinstance(location, float):
            initial_data["location"] = location

        dialog = BaliseConfigDialog(self, config_data=initial_data, max_length=self.get_max_length())
        if dialog.exec():
            if dialog.config_data:
                self.balises.append(dialog.config_data)
                self.config_manager.save_balises(self.balises)
                self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                                  reset_view=False, preserve_state=True)
                self.update_menus()

    def edit_balise(self, index):
        """
        编辑现有的应答器。
        
        Args:
            index (int): 要编辑的应答器在列表中的索引。
        """
        if 0 <= index < len(self.balises):
            dialog = BaliseConfigDialog(self, self.balises[index], max_length=self.get_max_length())
            if dialog.exec():
                self.balises[index] = dialog.config_data
                self.config_manager.save_balises(self.balises)
                self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                                  reset_view=False, preserve_state=True)
                self.update_menus()

    def delete_balise(self, index):
        """
        删除指定的应答器。
        
        Args:
            index (int): 要删除的应答器在列表中的索引。
        """
        if 0 <= index < len(self.balises):
            del self.balises[index]
            self.config_manager.save_balises(self.balises)
            self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                              reset_view=False, preserve_state=True)
            self.update_menus()

    def locate_balise(self, index):
        """
        在视图中定位指定的应答器。
        将视图中心移动到应答器位置并放大显示。
        
        Args:
            index (int): 应答器索引。
        """
        if 0 <= index < len(self.balises):
            balise = self.balises[index]
            try:
                location = float(balise.get("location", 0.0))
                # Use a larger zoom scale for clear visibility (300px/km)
                self.simulation_widget.center_on_location(location, zoom_scale=5000.0)
            except ValueError:
                print(f"Invalid location for balise {index}")

    def create_station(self):
        """
        创建新的车站。
        打开车站配置对话框，确认后保存并更新显示。
        """
        dialog = StationConfigDialog(self, max_length=self.get_max_length())
        if dialog.exec():
            if dialog.config_data:
                self.stations.append(dialog.config_data)
                self.config_manager.save_stations(self.stations)
                self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                                  reset_view=False)
                self.update_menus()

    def edit_station(self, index):
        """
        编辑现有的车站。
        
        Args:
            index (int): 要编辑的车站索引。
        """
        if 0 <= index < len(self.stations):
            dialog = StationConfigDialog(self, self.stations[index], max_length=self.get_max_length())
            if dialog.exec():
                self.stations[index] = dialog.config_data
                self.config_manager.save_stations(self.stations)
                self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                                  reset_view=False)
                self.update_menus()

    def delete_station(self, index):
        """
        删除指定的车站。
        
        Args:
            index (int): 要删除的车站索引。
        """
        if 0 <= index < len(self.stations):
            del self.stations[index]
            self.config_manager.save_stations(self.stations)
            self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                              reset_view=False)
            self.update_menus()

    def create_train(self):
        """
        创建新的列车。
        打开列车配置对话框，确认后保存并更新显示。
        """
        dialog = TrainConfigDialog(self, stations=self.stations)
        if dialog.exec():
            if dialog.config_data:
                self.trains.append(dialog.config_data)
                self.config_manager.save_trains(self.trains)
                self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                                  reset_view=False)
                self.update_menus()

    def edit_train(self, index):
        """
        编辑现有的列车。
        
        Args:
            index (int): 要编辑的列车索引。
        """
        if 0 <= index < len(self.trains):
            dialog = TrainConfigDialog(self, self.trains[index], stations=self.stations)
            if dialog.exec():
                self.trains[index] = dialog.config_data
                self.config_manager.save_trains(self.trains)
                self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                                  reset_view=False)
                self.update_menus()

    def delete_train(self, index):
        """
        删除指定的列车。
        
        Args:
            index (int): 要删除的列车索引。
        """
        if 0 <= index < len(self.trains):
            del self.trains[index]
            self.config_manager.save_trains(self.trains)
            self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                              reset_view=False)
            self.update_menus()

    def edit_line_config(self):
        """
        编辑线路全局配置。
        如线路总长度等。
        """
        dialog = LineConfigDialog(self, self.line_config)
        if dialog.exec():
            self.line_config = dialog.config_data
            self.config_manager.save_line_config(self.line_config)
            self.simulation_widget.set_config(self.balises, self.stations, self.trains, self.line_config,
                                              reset_view=False)

    def start_simulation(self):
        """
        开始仿真运行。
        """
        self.simulation_widget.start_simulation()
        self.statuslabel.setText("Status: RUN")

    def stop_simulation(self):
        """
        停止仿真运行。
        """
        self.simulation_widget.stop_simulation()
        self.statuslabel.setText("Status: STOP")

    def pause_simulation(self):
        """
        暂停或恢复仿真运行。
        """
        self.simulation_widget.pause_simulation()
        self.statuslabel.setText("Status: PAUSE")

    def save_all_config(self):
        """
        保存所有配置数据。
        包括应答器、车站、列车和线路配置。
        """
        self.config_manager.save_balises(self.balises)
        self.config_manager.save_stations(self.stations)
        self.config_manager.save_trains(self.trains)
        self.config_manager.save_line_config(self.line_config)

    def update_train_info(self, trains):
        """
        更新UI上的列车信息显示。
        
        Args:
            trains (list): 包含列车状态的列表。
        """
        info_text = ""
        for train in trains:
            name = train.get("name", "Unknown")
            speed = train.get("current_speed_limit", 100.0)
            info_text += f"{name} Speed: {speed} km/h\n"
        self.label_trains_speed.setText(info_text)

    def update_sim_time_label(self, sim_dt):
        """更新时间标签显示。"""
        if sim_dt:
            self.timelabel.setText(f"Time: {sim_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.timelabel.setText("Time: --")

    def open_map_scheduler(self):
        """打开运行图编辑窗口"""
        self.map_window = MapSchedulerWindow(self)
        self.map_window.show()

    def _load_last_map_data(self):
        """加载最近的运行图CSV数据"""
        settings = QSettings("BaliseTester", "MapScheduler")
        path = settings.value("last_file_path", "")
        if not path:
            default_path = os.path.join("data", "map", "1.csv")
            if os.path.exists(default_path):
                path = default_path

        if not path or not os.path.exists(path):
            return []

        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                data = list(reader)
                return data
        except Exception as e:
            print(f"Failed to load map file {path}: {e}")
            return []

    def open_map_preview(self):
        """打开运行图预览窗口"""
        data = self._load_last_map_data()
        line_length = self.get_max_length()
        self.map_preview = MapPreviewDialog(self, schedule_data=data, stations=self.stations, line_length=line_length)
        self.map_preview.show()

    def keyPressEvent(self, event):
        """
        处理键盘按下事件。
        空格键用于控制仿真的暂停和开始。
        END键用于停止仿真。
        
        Args:
            event (QKeyEvent): 键盘事件对象。
        """
        if event.key() == Qt.Key_Space:
            if self.simulation_widget.is_running:
                self.pause_simulation()
            else:
                self.start_simulation()
        elif event.key() == Qt.Key_End:
            self.stop_simulation()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """
        处理窗口关闭事件。
        关闭所有打开的子窗口。
        """
        # Close Map Scheduler if open
        if hasattr(self, 'map_window') and self.map_window:
            self.map_window.close()

        # Close Map Preview if open
        if hasattr(self, 'map_preview') and self.map_preview:
            self.map_preview.close()

        # Close About Window if open
        if self.about_window:
            self.about_window.close()

        # Accept the close event
        event.accept()

    def show_about_dialog(self):
        """ 显示关于对话框。 """
        if not self.about_window:
            self.about_window = AboutWindow()
        self.about_window.show()
        self.about_window.raise_()
        self.about_window.activateWindow()
