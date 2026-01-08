"""Map preview window module."""

import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QMessageBox,
                               QPushButton, QVBoxLayout, QCheckBox)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

# Set Chinese font support for Matplotlib
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MapPreviewDialog(QDialog):
    """Train schedule preview dialog using Matplotlib.

    Supports:
        - Ctrl+Scroll: Zoom.
        - Scroll: Vertical pan.
        - Shift+Scroll: Horizontal pan.
        - Ctrl+Shift+Scroll: X-axis zoom.
        - Auto-fit view.
    """

    def __init__(self, parent=None, schedule_data=None, stations=None, line_length=None):
        super().__init__(parent)
        self.setWindowTitle("列车运行图预览")
        self.resize(1000, 700)
        # Make dialog non-modal so other windows can be used
        self.setModal(False)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.schedule_data = schedule_data if schedule_data else []
        self.stations = stations if stations else []
        self.line_length = line_length if line_length else 100.0

        # Store original axis limits for auto-fit
        self.original_xlim = None
        self.original_ylim = None

        # Optimization: Text Data Storage
        self.all_text_data = []  # List of (time_num, loc, text)
        self.text_artists = []  # Current Text Artists

        # Debounce Timer for Label Rendering
        self.render_timer = QTimer(self)
        self.render_timer.setSingleShot(True)
        self.render_timer.setInterval(300)  # 300ms delay after interaction stops
        self.render_timer.timeout.connect(self.update_labels)

        self.layout = QVBoxLayout(self)

        # Chart Canvas
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Connect scroll event for zooming
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_release_event', self.on_interaction_end)

        # Buttons
        self.btn_layout = QHBoxLayout()

        self.chk_show_labels = QCheckBox("动态显示车次")
        self.chk_show_labels.setChecked(True)
        self.chk_show_labels.setToolTip("选中后，仅在缩放至局部或车次较少时显示标签，防止卡顿")
        self.chk_show_labels.stateChanged.connect(self.trigger_update_labels)

        self.btn_auto_fit = QPushButton("自适应大小")
        self.btn_auto_fit.clicked.connect(self.auto_fit_view)
        self.btn_close = QPushButton("关闭")
        self.btn_close.clicked.connect(self.close)
        self.btn_save = QPushButton("保存图片")
        self.btn_save.clicked.connect(self.save_plot)

        self.btn_layout.addWidget(self.chk_show_labels)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_auto_fit)
        self.btn_layout.addWidget(self.btn_save)
        self.btn_layout.addWidget(self.btn_close)
        self.layout.addLayout(self.btn_layout)

        self.plot_graph()

    def parse_time(self, time_str):
        """解析时间字符串 HH:MM:SS or HH:MM"""
        if not time_str or not isinstance(time_str, str):
            return None

        time_str = time_str.strip()
        if not time_str:
            return None

        formats = ["%H:%M:%S", "%H:%M"]
        # Use a fixed dummy date for time comparison
        base_date = datetime.datetime.now().date()

        for fmt in formats:
            try:
                t = datetime.datetime.strptime(time_str, fmt).time()
                return datetime.datetime.combine(base_date, t)
            except ValueError:
                continue
        return None

    def plot_graph(self):
        """绘制运行图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # 1. Prepare Y-Axis (Stations)
        # Use simple location based Y
        # Sort stations by location just in case
        sorted_stations = sorted(self.stations, key=lambda s: s.get("location", 0.0))

        # Extract names and locs
        station_locs = [s.get("location", 0.0) for s in sorted_stations]
        station_names = [s.get("name", f"Station {i}") for i, s in enumerate(sorted_stations)]

        if not sorted_stations:
            # Fallback if no stations provided
            ax.text(0.5, 0.5, "没有车站数据", ha='center', va='center')
            self.canvas.draw()
            return

        min_loc = min(station_locs)
        max_loc = max(station_locs)

        if self.line_length > max_loc:
            max_loc = self.line_length

        # 2. Prepare Data for Optimized Drawing
        segments = []
        points_x = []
        points_y = []
        texts = []
        train_color = "#E040FB"  # Bright purple

        all_times = []

        # 3. Process Schedule Data
        for row in self.schedule_data:
            if len(row) < 7:
                continue

            train_name = row[0]
            start_st_name = row[1]
            arr_start_str = row[2]
            dep_start_str = row[3]
            end_st_name = row[4]
            leave_end_str = row[5]
            arr_end_str = row[6]

            # Find Locations
            start_loc = next((s.get("location") for s in self.stations if s.get("name") == start_st_name), None)
            end_loc = next((s.get("location") for s in self.stations if s.get("name") == end_st_name), None)

            if start_loc is None or end_loc is None:
                continue

            # Parse Times
            t_arr_start = self.parse_time(arr_start_str)
            t_dep_start = self.parse_time(dep_start_str)
            t_leave_end = self.parse_time(leave_end_str)
            t_arr_end = self.parse_time(arr_end_str)

            # Helper to handle time crossing midnight relative to a base time
            def adjust_time(t, base):
                if t and base and t < base:
                    return t + datetime.timedelta(days=1)
                return t

            # Assuming strictly increasing time for the segment sequence:
            base_t = t_arr_start or t_dep_start or t_arr_end or t_leave_end
            if not base_t:
                continue

            # Adjust times sequentially
            current_base = base_t

            if t_arr_start:
                current_base = t_arr_start

            if t_dep_start:
                t_dep_start = adjust_time(t_dep_start, current_base)
                current_base = t_dep_start

            if t_arr_end:
                t_arr_end = adjust_time(t_arr_end, current_base)
                current_base = t_arr_end

            if t_leave_end:
                t_leave_end = adjust_time(t_leave_end, current_base)

            # Collect times for axis scaling
            times_in_row = [t for t in [t_arr_start, t_dep_start, t_arr_end, t_leave_end] if t]
            all_times.extend(times_in_row)

            # Collect Segments for LineCollection

            # 1. Dwell at Start (ArrStart -> DepStart)
            if t_arr_start and t_dep_start:
                s_num, e_num = mdates.date2num(t_arr_start), mdates.date2num(t_dep_start)
                segments.append([(s_num, start_loc), (e_num, start_loc)])
                points_x.extend([s_num, e_num])
                points_y.extend([start_loc, start_loc])

            # 2. Travel (DepStart -> ArrEnd)
            t_start_travel = t_dep_start
            t_end_travel = t_arr_end

            if t_start_travel and t_end_travel:
                start_num = mdates.date2num(t_start_travel)
                end_num = mdates.date2num(t_end_travel)
                # print(f"Processing travel: {train_name} from {start_num} to {end_num}") # Debug
                segments.append([(start_num, start_loc), (end_num, end_loc)])
                points_x.extend([start_num, end_num])
                points_y.extend([start_loc, end_loc])

                # Store text info but DO NOT DRAW YET
                mid_time_num = (start_num + end_num) / 2
                mid_loc = (start_loc + end_loc) / 2
                self.all_text_data.append((mid_time_num, mid_loc, train_name))

            # 3. Dwell at End (ArrEnd -> LeaveEnd)
            if t_arr_end and t_leave_end:
                s_num, e_num = mdates.date2num(t_arr_end), mdates.date2num(t_leave_end)
                segments.append([(s_num, end_loc), (e_num, end_loc)])
                points_x.extend([s_num, e_num])
                points_y.extend([end_loc, end_loc])

        # Batch Draw Lines using LineCollection
        if segments:
            lc = LineCollection(segments, colors=train_color, linewidths=2)
            ax.add_collection(lc)

        # Draw Markers - Optimized
        if points_x:
            ax.scatter(points_x, points_y, color=train_color, s=10, edgecolors='none', zorder=3)

        # Triggle Lazy Text Loading
        self.trigger_update_labels()

        # 4. Configure Axes
        # Y Axis
        ax.set_yticks(station_locs)
        ax.set_yticklabels(station_names)
        ax.set_ylim(max_loc + 1, min_loc - 1)  # Inverted Y axis as requested
        ax.set_ylabel("车站 / 里程 (km)")

        # X Axis - Fixed from 0:00 to 24:00
        ax.xaxis_date()
        ax.set_xlabel("时间")

        # Set fixed X Limits: 0:00 to 24:00
        base_date = datetime.datetime.now().date()
        time_start = datetime.datetime.combine(base_date, datetime.time(0, 0, 0))
        time_end = datetime.datetime.combine(base_date, datetime.time(23, 59, 59))
        ax.set_xlim(mdates.date2num(time_start), mdates.date2num(time_end))

        # Dynamic formatter
        self._update_time_axis_format(ax)

        # Grid
        ax.grid(True, linestyle='--', alpha=0.6)

        # Draw Horizontal dashed lines for stations
        if all_times and station_locs:
            xlims = ax.get_xlim()
            # Vectorsized hlines is faster
            ax.hlines(station_locs, xlims[0], xlims[1], colors='gray', linestyles=':', linewidth=0.5, alpha=0.5)

        self.figure.tight_layout()

        # Store original limits for auto-fit
        self.original_xlim = ax.get_xlim()
        self.original_ylim = ax.get_ylim()

        self.canvas.draw()

    def _update_time_axis_format(self, ax=None):
        """根据X轴时间跨度动态调整时间显示格式"""
        if ax is None:
            if not self.figure.axes:
                return
            ax = self.figure.axes[0]

        xlim = ax.get_xlim()
        # Convert matplotlib date numbers to timedelta
        span_days = xlim[1] - xlim[0]
        span_seconds = span_days * 24 * 3600

        # Choose format based on visible time span
        if span_seconds <= 120:  # <= 2 minutes: show seconds
            fmt = '%H:%M:%S'
        elif span_seconds <= 600:  # <= 10 minutes: show seconds
            fmt = '%H:%M:%S'
        elif span_seconds <= 3600:  # <= 1 hour: show minutes
            fmt = '%H:%M'
        else:  # > 1 hour: show hours and minutes
            fmt = '%H:%M'

        ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))

    def on_scroll(self, event):
        """Handle scroll event for panning and zooming."""
        self.trigger_update_labels()  # Restart timer on scroll

        if event.inaxes is None:
            return

        ax = event.inaxes
        modifiers = QApplication.keyboardModifiers()

        # Determine scroll direction
        if event.button == 'up':
            direction = 1
        elif event.button == 'down':
            direction = -1
        else:
            return

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        ctrl_pressed = modifiers & Qt.ControlModifier
        shift_pressed = modifiers & Qt.ShiftModifier

        if ctrl_pressed and shift_pressed:
            # Ctrl+Shift+Scroll: Zoom X axis only
            base_scale = 1.2
            scale_factor = 1 / base_scale if direction == 1 else base_scale

            xdata = event.xdata
            new_width = (xlim[1] - xlim[0]) * scale_factor
            relx = (xdata - xlim[0]) / (xlim[1] - xlim[0])

            ax.set_xlim([xdata - new_width * relx, xdata + new_width * (1 - relx)])
            self._update_time_axis_format(ax)

        elif ctrl_pressed:
            # Ctrl+Scroll: Zoom both axes
            base_scale = 1.2
            scale_factor = 1 / base_scale if direction == 1 else base_scale

            xdata = event.xdata
            ydata = event.ydata

            new_width = (xlim[1] - xlim[0]) * scale_factor
            new_height = (ylim[1] - ylim[0]) * scale_factor

            relx = (xdata - xlim[0]) / (xlim[1] - xlim[0])
            rely = (ydata - ylim[0]) / (ylim[1] - ylim[0])

            ax.set_xlim([xdata - new_width * relx, xdata + new_width * (1 - relx)])
            ax.set_ylim([ydata - new_height * rely, ydata + new_height * (1 - rely)])
            self._update_time_axis_format(ax)

        elif shift_pressed:
            # Shift+Scroll: Horizontal pan (left/right)
            pan_amount = (xlim[1] - xlim[0]) * 0.1 * direction
            ax.set_xlim(xlim[0] - pan_amount, xlim[1] - pan_amount)
            self._update_time_axis_format(ax)

        else:
            # Plain Scroll: Vertical pan (up/down)
            pan_amount = (ylim[1] - ylim[0]) * 0.1 * direction
            ax.set_ylim(ylim[0] + pan_amount, ylim[1] + pan_amount)

        self.canvas.draw_idle()

    def on_interaction_end(self, event):
        """Handle interaction end (mouse release/button release)."""
        self.trigger_update_labels()

    def trigger_update_labels(self):
        """Start/Restart debounce timer for label update."""
        self.render_timer.start()

    def update_labels(self):
        """Update visible text labels based on current view and UI settings."""
        if not self.figure.axes:
            return
        ax = self.figure.axes[0]

        # 1. Check if labels are enabled
        if not self.chk_show_labels.isChecked():
            # Clear all current texts
            if self.text_artists:
                for t in self.text_artists:
                    t.remove()
                self.text_artists.clear()
                self.canvas.draw_idle()
            return

        # 2. Get Visible Range and Current Limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # 3. Filter Visible Data
        # Optimization: Don't reiterate if data is massive and fully zoomed out
        # Heuristic: Check density.

        visible_candidates = []

        # Safe check for ylim (since it might be inverted)
        min_y, max_y = sorted(ylim)

        for time_num, loc, text in self.all_text_data:
            if xlim[0] <= time_num <= xlim[1] and min_y <= loc <= max_y:
                visible_candidates.append((time_num, loc, text))

        # 4. Limit Number of Labels
        MAX_LABELS = 100  # Adjust this threshold for performance

        should_draw = len(visible_candidates) <= MAX_LABELS

        # If too many labels, maybe just clear?
        # Or maybe check zoom level?
        # Let's enforce the limit to keep it fast.

        # Remove Old Artists
        for t in self.text_artists:
            t.remove()
        self.text_artists.clear()

        if should_draw:
            for time_num, loc, txt in visible_candidates:
                t = ax.text(time_num, loc, txt, fontsize=8, color='black',
                            bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7),
                            clip_on=True)
                self.text_artists.append(t)

        self.canvas.draw_idle()

    def auto_fit_view(self):
        """恢复到自适应大小视图（X轴0:00-24:00）"""
        if not self.figure.axes:
            return

        ax = self.figure.axes[0]

        # Reset to fixed 0:00-24:00 X range
        base_date = datetime.datetime.now().date()
        time_start = datetime.datetime.combine(base_date, datetime.time(0, 0, 0))
        time_end = datetime.datetime.combine(base_date, datetime.time(23, 59, 59))
        ax.set_xlim(mdates.date2num(time_start), mdates.date2num(time_end))

        if self.original_ylim:
            ax.set_ylim(self.original_ylim)
        self._update_time_axis_format(ax)
        self.canvas.draw_idle()

    def save_plot(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "保存图片", "train_graph.png", "PNG Images (*.png)")
        if path:
            self.figure.savefig(path, dpi=300)
            QMessageBox.information(self, "信息", f"图片已保存到 {path}")
