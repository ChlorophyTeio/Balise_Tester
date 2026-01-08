"""Simulation widget module for train operation simulation."""

import copy
import csv
import datetime
import os
import sys
from typing import Dict, List, Optional

from PySide6.QtCore import QPoint, QPointF, QRect, QSettings, Qt, QTimer, Signal
from PySide6.QtGui import (QColor, QFont, QPainter, QPen, QPixmap,
                           QPolygonF)
from PySide6.QtWidgets import QToolTip, QWidget

from ..core.logger import SimulationLogger
from ..core.packet_utils import PACKET_TYPE_MAP, PacketUtils, decode_packet


class SimulationWidget(QWidget):
    """Widget for visualizing and simulating train movements and balise interactions."""

    trains_updated = Signal(list)
    balise_create_requested = Signal(float)
    balise_edit_requested = Signal(int)
    # Signal emitted when a balise is dragged to a new location: (index, new_location_float)
    balise_moved = Signal(int, float)
    sim_time_updated = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize simulation widget.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setMouseTracking(True)
        self.balises = []
        self.stations = []
        self.trains = []
        self.line_config = {}
        self.track_length = 100.0  # Default 100km
        self.scale = 10.0  # pixels per km
        self.offset_x = 50
        self.offset_y = 300

        # Path resolution
        if getattr(sys, 'frozen', False):
            # Running in a bundle
            self.project_root = sys._MEIPASS
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # current_dir is .../balise_tester/widgets
            # Up 2 levels -> .../Balise_Tester
            self.project_root = os.path.dirname(os.path.dirname(current_dir))

        asset_dir = os.path.join(self.project_root, "assets", "img")
        self.balise_n_img = QPixmap(os.path.join(asset_dir, "balise_n.png"))
        self.balise_a_img = QPixmap(os.path.join(asset_dir, "balise_a.png"))
        self.train_img = QPixmap(os.path.join(asset_dir, "train.png"))

        # Logger
        self.logger = SimulationLogger()

        # Simulation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.is_running = False
        self.timer_interval = 16  # approx 60 FPS

        # Simulation time clock (for timetable based runs)
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.tick_sim_time)
        self.current_sim_time = None

        # Timetable file tracking
        self.last_schedule_mtime = None

        # Timetable data
        self.schedule_entries = []  # Parsed schedule definitions
        self.schedule_runtime = []  # Per-run mutable state
        self.schedule_loaded = False
        self.train_templates = []

        # Initialize timetable and timers so schedule trains stay independent of run/pause state
        self.load_schedule_entries()
        now_cutoff = datetime.datetime.now().replace(microsecond=0)
        self._reset_schedule_state(start_time=now_cutoff)
        self.initialize_sim_clock()
        self._update_schedule_trains()

        self.timer.start(self.timer_interval)
        self.time_timer.start(1000)

        # View control
        self.auto_fit = True
        self.is_panning = False
        self.follow_train_mode = False
        self.last_mouse_pos = QPoint()

        # Dragging state
        self.is_dragging_balise = False
        self.dragged_balise_index = -1
        self.drag_start_mouse_pos = QPoint()
        self.has_dragged = False

        # Track last pass time for exit balises to handle signal delay
        # Key: balise_index, Value: timestamp (datetime)
        self.balise_pass_times = {}

        # Enable keyboard focus for the "Jump" easter egg
        self.setFocusPolicy(Qt.StrongFocus)

        # Hover state for live tooltip updates
        self.hovered_balise_index = -1
        self.cursor_global_pos = None
        self.last_tooltip_text = ""

    def set_config(
            self,
            balises: List[Dict],
            stations: List[Dict],
            trains: List[Dict],
            line_config: Optional[Dict] = None,
            reset_view: bool = True,
            preserve_state: bool = False,
    ):
        """Load configuration data into the simulation.

        Args:
            balises: List of balise configuration dictionaries.
            stations: List of station configuration dictionaries.
            trains: List of train configuration dictionaries.
            line_config: Line configuration (e.g., total length).
            reset_view: Whether to auto-fit the camera view.
            preserve_state: Whether to preserve current simulation state (train positions).
        """
        self.balises = copy.deepcopy(balises)
        self.stations = copy.deepcopy(stations)

        # If balise list changes length or identity, indices in balise_pass_times are invalid.
        # However, set_config is usually called with preserve_state=False on load.
        # If preserve_state=True (e.g. modifying property), indices might match if list order is same.
        # But for safety, if we don't preserve state (load/new), clear it.
        # If preserving state (edit), we hope indices align. 
        # But wait, if we edit balises, the list is replaced. Indices might shift if inserted/deleted.
        # If just property edit, fine.
        # Given "preserve_state" is mainly for "don't reset trains", we should ideally be careful.
        # But the original bug was stale times.
        if not preserve_state:
            self.balise_pass_times.clear()

        # Use a private copy to avoid polluting persisted config with runtime-only trains
        if not preserve_state:
            self.trains = copy.deepcopy(trains)
        else:
            # If preserving state, we don't overwrite self.trains with the config list
            # because self.trains currently holds the active/running train objects.
            pass

        self.train_templates = copy.deepcopy(trains)
        self.line_config = line_config or {}

        # Reload schedule entries only if first load or explicitly resetting
        if not self.schedule_entries or not preserve_state:
            self.load_schedule_entries()

        if not preserve_state:
            # Initialize jump state for trains only if resetting or strictly needed
            for train in self.trains:
                train["is_jumping"] = False
                train["jump_h"] = 0.0
                train["jump_v"] = 0.0
                train["active_restrictions"] = []  # Type: List[Dict: {type, start_km, end_km, speed, priority}]

        # Determine track length
        if line_config and "total_length" in line_config:
            self.track_length = float(line_config["total_length"])
        else:
            # Calculate track length based on max location if not configured
            max_loc = 0
            for b in balises:
                max_loc = max(max_loc, b.get("location", 0))
            for s in stations:
                max_loc = max(max_loc, s.get("location", 0))
            self.track_length = max(max_loc + 10, 20)  # At least 20km

        if not preserve_state:
            self.reset_train_positions()
            self.balise_pass_times.clear()  # Clear pass history on new config

        self._process_balise_ids()

        if reset_view:
            self.auto_fit = True

        # Refresh timetable trains with latest templates/config
        # Only reset if we are not preserving state (e.g. balise edit)
        if self.schedule_entries and not preserve_state:
            now_cutoff = self.current_sim_time or datetime.datetime.now().replace(microsecond=0)
            self._reset_schedule_state(start_time=now_cutoff)
            self.initialize_sim_clock()
            self._update_schedule_trains()

        self.update()

    def _process_balise_ids(self):
        """Process balise ID logic.

        Groups balises by father_balise, assigns missing sub_ids sequentially,
        and calculates n_total and q_link fields.
        """
        # Group balises by father_balise
        groups = {}
        for balise in self.balises:
            father_id = str(balise.get("father_balise", "")).strip()
            if father_id:
                if father_id not in groups:
                    groups[father_id] = []
                groups[father_id].append(balise)
            else:
                # No father, treat as single
                balise["sub_id"] = "0"
                balise["n_total"] = "1"
                balise["q_link"] = "0"

        # Process groups
        for father_id, group in groups.items():
            # Sort by location to have a consistent order if needed, or just keep order
            # User said: "一组内的应答器自编号从0开始，若有应答器处于组内为填写则自动分配子编号"
            # First, check existing sub_ids
            used_ids = set()
            for b in group:
                sid = str(b.get("sub_id", "")).strip()
                if sid.isdigit():
                    used_ids.add(int(sid))

            next_id = 0
            for b in group:
                sid = str(b.get("sub_id", "")).strip()
                if not sid or not sid.isdigit():
                    while next_id in used_ids:
                        next_id += 1
                    b["sub_id"] = str(next_id)
                    used_ids.add(next_id)

            # Assign n_total and q_link
            count = len(group)
            for b in group:
                b["n_total"] = str(count)
                if count >= 2:
                    b["q_link"] = "1"
                else:
                    b["q_link"] = "0"

    # ---- Timetable helpers ----

    def _parse_time_value(self, value, base_date):
        """Parse HH:MM or HH:MM:SS into a datetime on base_date."""
        if not value or not isinstance(value, str):
            return None
        value = value.strip()
        if not value:
            return None

        for fmt in ["%H:%M:%S", "%H:%M"]:
            try:
                t = datetime.datetime.strptime(value, fmt).time()
                return datetime.datetime.combine(base_date, t)
            except ValueError:
                continue
        return None

    def _station_location(self, name):
        """Return station km location by name."""
        for s in self.stations:
            if s.get("name") == name:
                return s.get("location", 0.0)
        return None

    def _get_train_template(self, name):
        """Find a train config template by name."""
        for t in self.train_templates:
            if t.get("name") == name:
                return copy.deepcopy(t)
        return None

    def _get_station_exit_balise(self, station_name):
        """Find the active exit balise for a given station.
        
        Criteria: Type=1 (Active) AND Name contains (Station Name + "CZ").
        """
        if not station_name:
            return None, None

        for i, balise in enumerate(self.balises):
            name = balise.get("name", "")
            b_type = str(balise.get("type", "0"))

            # Check criteria
            if b_type == "1" and station_name in name and "CZ" in name:
                return i, balise

        return None, None

    def _get_effective_balise_packets(self, balise_index, current_time=None):
        """Determine the effective packets for a balise based on schedule state.
        
        Logic:
        1. If no CTCS-5 in config -> Always Green (return all packets).
        2. If CTCS-5 exists -> Default is Red (CTCS-5 Only).
        3. Turn Green (All packets excluding CTCS-5) if:
           - A train is leaving (now >= leave_time).
           - AND the train passed recently (< 2s ago).
        """
        balise = self.balises[balise_index]
        all_packets = copy.deepcopy(balise)

        # If no CTCS-5 configured, logic doesn't apply
        if "CTCS-5" not in balise or not str(balise["CTCS-5"]).strip():
            return all_packets

        current_dt = current_time or datetime.datetime.now()

        # Check if authorized to be Green
        is_green = False

        # Check overlap with authorization window
        # We need to find a train that uses this station/balise
        # Optimization: We only check if we have a recorded 'pass' time that is very recent
        # BUT the requirement says "Departure sends other packets".
        # Before passing, the train is AT the station (or approaching).
        # We need to know if a train is *currently authorized* to pass.

        # Search for a relevant authorized train
        for train in self.trains:
            # Determine if this is a scheduled train or manual
            is_scheduled = train.get("schedule_managed", False)

            # Check station relevance
            s_station = train.get("start_station")
            e_station = train.get("end_station")

            # Helper to safely get location
            def get_loc(key, name):
                val = train.get(key)
                if val is not None: return float(val)
                return self._station_location(name)

            t_start = get_loc("start_loc", s_station)
            t_end = get_loc("end_loc", e_station)

            # Check if this balise belongs to start or end station
            b_name = balise.get("name", "")
            b_loc = float(balise.get("location", 0.0))

            relevant = False
            target_leave_time = None
            should_stop = False  # For manual trains at end station

            if s_station and s_station in b_name and "CZ" in b_name:
                relevant = True
                # Start station: authorized to leave
                if is_scheduled:
                    target_leave_time = train.get("dep_start") or train.get("dep_time")
            elif e_station and e_station in b_name and "CZ" in b_name:
                relevant = True
                # End station:
                if is_scheduled:
                    target_leave_time = train.get("leave_end") or train.get("leave_time")
                else:
                    # Manual train ending here -> Should Stop (Red)
                    should_stop = True
            else:
                # Case 3: Intermediate (On Route)
                if t_start is not None and t_end is not None:
                    min_loc = min(t_start, t_end)
                    max_loc = max(t_start, t_end)

                    if min_loc < b_loc < max_loc:
                        relevant = True
                        if is_scheduled:
                            target_leave_time = train.get("dep_start") or train.get("dep_time")

            if relevant:
                if should_stop:
                    # Manual train at destination: Keep Red (CTCS-5)
                    # Do not set is_green = True
                    continue

                if is_scheduled and target_leave_time:
                    # Scheduled Logic
                    if current_dt >= target_leave_time:
                        last_pass = self.balise_pass_times.get(balise_index)

                        if not last_pass:
                            is_green = True
                        elif last_pass < target_leave_time:
                            is_green = True
                        else:
                            delta = (current_dt - last_pass).total_seconds()
                            if delta < 3.0:
                                is_green = True
                elif not is_scheduled:
                    # Manual Train Logic
                    # Start or Intermediate -> Green authorized immediately
                    # Logic: Green until passed + 3s
                    last_pass = self.balise_pass_times.get(balise_index)

                    if not last_pass:
                        is_green = True
                    else:
                        delta = (current_dt - last_pass).total_seconds()
                        if delta < 3.0:
                            is_green = True

                if is_green:
                    break

        if is_green:
            # Remove CTCS-5, keep others
            # Also hide any packet that has empty value
            final_packets = {}
            for k, v in all_packets.items():
                if k == "CTCS-5": continue
                # Basic fields or non-empty packets
                if str(v).strip():
                    final_packets[k] = v
            return final_packets
        else:
            # Keep ONLY CTCS-5 for Red, but preserve all header info
            # We remove other packet types from the copy
            keys_to_remove = [k for k in PACKET_TYPE_MAP.keys() if k != "CTCS-5"]
            for k in keys_to_remove:
                if k in all_packets:
                    del all_packets[k]
            return all_packets

    def load_schedule_entries(self):
        """Load timetable from the last used CSV (if any)."""
        settings = QSettings("BaliseTester", "MapScheduler")
        path = settings.value("last_file_path", "")

        # Fallback to default sample
        if not path:
            default_path = os.path.join(self.project_root, "data", "map", "1.csv")
            if os.path.exists(default_path):
                path = default_path

        if not path or not os.path.exists(path):
            self.schedule_entries = []
            return

        try:
            self.last_schedule_mtime = os.path.getmtime(path)
        except Exception:
            self.last_schedule_mtime = None

        base_date = datetime.date.today()
        entries = []
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) < 7:
                        continue

                    train_name = row[0].strip() if row[0] else "Train"
                    start_station = row[1].strip()
                    end_station = row[4].strip()

                    start_loc = self._station_location(start_station)
                    end_loc = self._station_location(end_station)
                    if start_loc is None or end_loc is None:
                        continue

                    arr_start = self._parse_time_value(row[2], base_date)
                    dep_start = self._parse_time_value(row[3], base_date)
                    leave_end = self._parse_time_value(row[5], base_date)
                    arr_end = self._parse_time_value(row[6], base_date)

                    # Ensure chronological order by rolling over to next day if needed
                    times = [arr_start, dep_start, arr_end, leave_end]
                    prev = None
                    for idx, t in enumerate(times):
                        if t is None:
                            continue
                        if prev and t < prev:
                            times[idx] = t + datetime.timedelta(days=1)
                        prev = times[idx]

                    arr_start, dep_start, arr_end, leave_end = times

                    # Handle Exit Balise Logic for Start/End Locations
                    # User Request: Train start/stop should be at Station Location, not Balise Location.
                    # Removed balise location override.

                    actual_start_loc = start_loc
                    actual_end_loc = end_loc

                    entries.append({
                        "train_name": train_name,
                        "start_station": start_station,
                        "end_station": end_station,
                        "start_loc": float(actual_start_loc),
                        "end_loc": float(actual_end_loc),
                        "arr_start": arr_start,
                        "dep_start": dep_start or arr_start,
                        "arr_end": arr_end,
                        "leave_end": leave_end or arr_end,
                        "created": False,
                        "removed": False,
                        "train_ref": None
                    })
        except Exception:
            entries = []

        self.schedule_entries = entries
        self.schedule_loaded = True

    def _maybe_reload_schedule(self):
        """Reload timetable if the source file changed on disk."""
        settings = QSettings("BaliseTester", "MapScheduler")
        path = settings.value("last_file_path", "")
        if not path:
            default_path = os.path.join(self.project_root, "data", "map", "1.csv")
            if os.path.exists(default_path):
                path = default_path

        if not path or not os.path.exists(path):
            return

        try:
            mtime = os.path.getmtime(path)
        except Exception:
            return

        if self.last_schedule_mtime is None or mtime > self.last_schedule_mtime:
            self.load_schedule_entries()
            now_cutoff = datetime.datetime.now().replace(microsecond=0)
            self._reset_schedule_state(start_time=now_cutoff)
            self.initialize_sim_clock()
            self._update_schedule_trains()

    def _reset_schedule_state(self, start_time=None):
        """Reset runtime state for timetable trains."""
        # Remove schedule-managed trains from the scene
        self.trains = [t for t in self.trains if not t.get("schedule_managed")]
        self.schedule_runtime = []

        for entry in self.schedule_entries:
            runtime_entry = copy.deepcopy(entry)
            runtime_entry["created"] = False
            runtime_entry["removed"] = False
            runtime_entry["train_ref"] = None

            # Skip entries fully expired before simulation start
            cutoff = start_time or datetime.datetime.now()
            leave_t = runtime_entry.get("leave_end") or runtime_entry.get("arr_end")
            if leave_t and leave_t < cutoff:
                runtime_entry["removed"] = True

            self.schedule_runtime.append(runtime_entry)

        self.current_sim_time = None

    def initialize_sim_clock(self):
        """Initialize simulation clock to real current time (no fast-forward)."""
        self.current_sim_time = datetime.datetime.now().replace(microsecond=0)

    def tick_sim_time(self):
        """Advance the simulation clock when running."""
        # Always follow real wall-clock time
        self._maybe_reload_schedule()
        self.current_sim_time = datetime.datetime.now().replace(microsecond=0)
        self._update_schedule_trains()
        self.sim_time_updated.emit(self.current_sim_time)

    def _create_schedule_train(self, entry):
        """Instantiate a train for the given timetable entry, using template config if available."""
        base_speed = float(self.line_config.get("max_speed", 350.0))

        template = self._get_train_template(entry["train_name"])
        train = template if template else {}

        # Set/override core fields
        train["name"] = entry["train_name"]
        train["start_station"] = entry["start_station"]
        train["end_station"] = entry["end_station"]
        train["current_location"] = entry["start_loc"]
        train["current_speed_limit"] = 0.0
        train.setdefault("active_restrictions", [])

        # Base speed: template initial_speed else line max
        if "initial_speed" in train:
            try:
                base_speed = float(train.get("initial_speed", base_speed))
            except ValueError:
                base_speed = float(self.line_config.get("max_speed", 350.0))
        train["base_speed"] = base_speed

        dep = entry.get("dep_start")
        arr = entry.get("arr_end")
        leave_t = entry.get("leave_end")

        # If train is already in-progress at sim start, place it proportionally
        sim_t = self.current_sim_time or dep
        if dep and arr and arr > dep and sim_t and sim_t > dep:
            total_seconds = (arr - dep).total_seconds()
            progress = (sim_t - dep).total_seconds() / total_seconds if total_seconds > 0 else 1.0
            progress = max(0.0, min(1.0, progress))
            train["current_location"] = entry["start_loc"] + (entry["end_loc"] - entry["start_loc"]) * progress

        train["schedule_managed"] = True
        train["status"] = "waiting"
        train["start_loc"] = entry["start_loc"]
        train["end_loc"] = entry["end_loc"]
        train["dep_time"] = dep
        train["arr_time"] = arr
        train["leave_time"] = leave_t
        train["planned_speed"] = base_speed

        self.trains.append(train)
        entry["created"] = True
        entry["train_ref"] = train
        self.trains_updated.emit(self.trains)

    def _update_schedule_trains(self):
        """Create or remove trains according to the timetable."""
        if not self.schedule_runtime or self.current_sim_time is None:
            return

        # Create trains that should now exist
        for entry in self.schedule_runtime:
            if entry.get("created") or entry.get("removed"):
                continue

            trigger_time = entry.get("arr_start") or entry.get("dep_start") or entry.get("arr_end") or entry.get(
                "leave_end")
            leave_time = entry.get("leave_end") or entry.get("arr_end")
            if leave_time and self.current_sim_time >= leave_time:
                entry["removed"] = True
                continue

            if trigger_time and self.current_sim_time >= trigger_time:
                self._create_schedule_train(entry)

        # Remove trains whose lifecycle ended
        to_remove = []
        for entry in self.schedule_runtime:
            if not entry.get("created") or entry.get("removed"):
                continue

            leave_time = entry.get("leave_end") or entry.get("arr_end")
            if leave_time and self.current_sim_time >= leave_time:
                train_obj = entry.get("train_ref")
                if train_obj:
                    to_remove.append(train_obj)
                entry["removed"] = True

        if to_remove:
            self.trains = [t for t in self.trains if t not in to_remove]
            self.trains_updated.emit(self.trains)

    def reset_train_positions(self):
        """
        重置所有列车到初始位置和速度。
        初始位置基于配置的 `start_station`。
        """
        for train in self.trains:
            if train.get("schedule_managed"):
                continue
            start_station_name = train.get("start_station", "")
            end_station_name = train.get("end_station", "")

            start_loc = 0.0
            end_loc = self.track_length  # Default end

            if start_station_name and start_station_name != "根据运行图运行":
                loc = self._station_location(start_station_name)
                if loc is not None: start_loc = loc

            if end_station_name and end_station_name != "根据运行图运行":
                loc = self._station_location(end_station_name)
                if loc is not None: end_loc = loc

            train["current_location"] = start_loc
            train["start_loc"] = start_loc
            train["end_loc"] = end_loc

            # Set initial speed
            initial_speed = float(train.get("initial_speed", 0.0))
            train["current_speed_limit"] = initial_speed
            default_max = float(self.line_config.get("max_speed", 350.0))
            train["base_speed"] = initial_speed if initial_speed > 0 else default_max
            train["active_restrictions"] = []

        self.trains_updated.emit(self.trains)

    def set_follow_mode(self, enabled):
        """
        设置是否开启列车追踪模式。
        
        参数:
            enabled (bool): True 开启，False 关闭。
        """
        self.follow_train_mode = enabled
        if enabled:
            self.auto_fit = False
            self.update_follow_offset()
            self.update()

    def update_follow_offset(self):
        """
        更新视图偏移量以保持列车在屏幕特定位置（追踪模式）。
        默认保持列车在屏幕左侧 1/4 处。
        """
        if not self.trains:
            return
        # Follow the first train
        train = self.trains[0]
        loc = train.get("current_location", 0)

        # Target position: 1/4 of window width
        target_x = self.width() * 0.25

        # offset_x = target_x - loc * scale
        self.offset_x = target_x - loc * self.scale

    def start_simulation(self):
        """开始仿真定时器。"""
        if self.is_running:
            return

        self.is_running = True

    def stop_simulation(self):
        """停止仿真，重置状态。"""
        self.is_running = False
        self.reset_train_positions()
        self.balise_pass_times.clear()  # Clear pass history
        if self.follow_train_mode:
            self.update_follow_offset()
        self.update()

    def pause_simulation(self):
        """暂停仿真（不重置状态）。"""
        self.is_running = False

    def update_simulation(self):
        """
        定时器触发的仿真步进函数。
        
        执行：
        1. 更新列车位置（基于物理步进）。
        2. 检测应答器经过事件。
        3. 处理彩蛋物理逻辑（跳跃）。
        4. 循环重置列车位置。
        """
        # Update train positions
        for train in self.trains:
            # Ensure position field exists
            if "current_location" not in train:
                train["current_location"] = 0.0

            # Timetable-driven trains always update (independent of run/pause)
            if train.get("schedule_managed"):
                sim_t = self.current_sim_time or datetime.datetime.now()
                old_pos = train.get("current_location", 0.0)
                new_pos = old_pos

                dep = train.get("dep_time")
                arr = train.get("arr_time")
                leave = train.get("leave_time")
                start_loc = train.get("start_loc", old_pos)
                end_loc = train.get("end_loc", old_pos)

                status = train.get("status", "waiting")

                # Before departure: hold position/speed zero
                if status == "waiting":
                    train["current_speed_limit"] = 0.0
                    if dep and sim_t >= dep:
                        status = "traveling"

                if status == "traveling":
                    # Move using standard step
                    self.check_restrictions(train)
                    current_speed_limit = float(train.get("current_speed_limit", train.get("base_speed", 100.0)))
                    if current_speed_limit <= 0:
                        current_speed_limit = float(train.get("base_speed", 100.0))

                    base_step = 0.1 * (self.timer_interval / 100.0)
                    step = base_step * (current_speed_limit / 100.0)

                    new_pos = old_pos + step if end_loc >= start_loc else old_pos - step

                    # Clamp to destination
                    if (end_loc >= start_loc and new_pos >= end_loc) or (end_loc < start_loc and new_pos <= end_loc):
                        new_pos = end_loc
                        status = "at_terminal"
                        train["current_speed_limit"] = 0.0
                    else:
                        # Apply restrictions mid-run
                        self.check_restrictions(train)

                    # Time-based arrival safeguard
                    if arr and sim_t >= arr:
                        new_pos = end_loc
                        status = "at_terminal"
                        train["current_speed_limit"] = 0.0

                if status == "at_terminal":
                    new_pos = end_loc
                    train["current_speed_limit"] = 0.0
                    if leave and sim_t >= leave:
                        status = "finished"

                train["status"] = status
                train["current_location"] = new_pos

                # Balise detection for timetable trains
                self._process_balise_crossing(train, old_pos, new_pos)
                continue

            # Manual trains only move when simulation is running
            if not self.is_running:
                continue

            old_pos = train["current_location"]

            # Revised step calculation for smoothness
            current_speed_limit = float(train.get("current_speed_limit", 100.0))
            base_step = 0.1 * (self.timer_interval / 100.0)
            step = base_step * (current_speed_limit / 100.0)

            train["current_location"] += step
            new_pos = train["current_location"]

            # Recalculate speed limit based on active restrictions
            self.check_restrictions(train)

            # Check for balises
            self._process_balise_crossing(train, old_pos, new_pos)

            # Determine limit location (Destination or Track End)
            # Default to track_length if end_loc not set or invalid
            limit_loc = train.get("end_loc")
            if limit_loc is None:
                limit_loc = self.track_length

            if train["current_location"] >= limit_loc:
                action = int(train.get("end_action", 0))  # 0:Stop, 2:Restart

                if action == 2:  # Restart
                    start_loc = train.get("start_loc", 0.0)
                    train["current_location"] = start_loc

                    # Reset Speed
                    default_max = float(self.line_config.get("max_speed", 350.0))
                    initial_speed = float(train.get("initial_speed", 0.0))
                    new_base = initial_speed if initial_speed > 0 else default_max

                    train["base_speed"] = new_base
                    train["current_speed_limit"] = new_base
                    train["active_restrictions"] = []
                else:
                    # Stop (or Turnback - treated as stop here)
                    train["current_location"] = limit_loc
                    train["current_speed_limit"] = 0.0
                    train["base_speed"] = 0.0
                    train["active_restrictions"] = []

            # Easter Egg: Jump Physics
            if train.get("is_jumping", False):
                train["jump_h"] += train["jump_v"]
                train["jump_v"] -= 2.0  # Gravity
                if train["jump_h"] <= 0:
                    train["jump_h"] = 0
                    train["is_jumping"] = False
                    train["jump_v"] = 0

        # Update tooltip if something changed while hovering (live update)
        if self.hovered_balise_index != -1 and self.cursor_global_pos:
            effective = self._get_effective_balise_packets(self.hovered_balise_index, self.current_sim_time)
            info = self.get_balise_tooltip_text(effective)
            if info != self.last_tooltip_text:
                QToolTip.showText(self.cursor_global_pos, info, self)
                self.last_tooltip_text = info

        if self.follow_train_mode:
            self.update_follow_offset()

        self.trains_updated.emit(self.trains)
        self.update()

    def _process_balise_crossing(self, train, old_pos, new_pos):
        """Check and process balises passed between two positions."""
        start = min(old_pos, new_pos)
        end = max(old_pos, new_pos)
        for i, balise in enumerate(self.balises):
            b_loc = balise.get("location", 0)
            if start <= b_loc <= end:
                # Skip if in jump
                if train.get("jump_h", 0) > 0:
                    continue

                # Record pass time for Exit Balises logic
                self.balise_pass_times[i] = self.current_sim_time or datetime.datetime.now()

                self.handle_balise_pass(train, balise, i)

    def check_restrictions(self, train):
        """
        检查并应用列车的速度限制。
        移除已过期的限制，并计算当前有效限速。
        """
        loc = train.get("current_location", 0.0)
        restrs = train.get("active_restrictions", [])

        # Filter expired
        valid_restrs = []
        for r in restrs:
            # check end condition: end_km present and passed
            if r["end_km"] is not None and loc > r["end_km"]:
                continue
            valid_restrs.append(r)

        train["active_restrictions"] = valid_restrs

        # Calculate speed
        default_max = float(self.line_config.get("max_speed", 350.0))
        base = train.get("base_speed", default_max)
        limit = base

        for r in valid_restrs:
            if loc >= r["start_km"]:
                if r["speed"] < limit:
                    limit = r["speed"]

        train["current_speed_limit"] = limit

    def handle_balise_pass(self, train: Dict, balise: Dict, index: int = -1):
        """Process logic when a train passes a balise.

        Decodes packets and updates speed restrictions.

        Args:
            train: Train configuration object.
            balise: Balise configuration object.
            index: Balise index in storage.
        """
        b_loc = balise.get("location", 0.0)
        log_packets = []

        # Determine effective packets based on schedule state
        effective_balise = balise
        if index >= 0:
            effective_balise = self._get_effective_balise_packets(index, self.current_sim_time)

        # 1. CTCS-5 (Absolute Stop) - Custom Logic
        # If effective packets contain CTCS-5, it means RED signal.
        if "CTCS-5" in effective_balise:
            # Just log it, usually implies emergency stop or red signal
            log_packets.append("CTCS-5 (Absolute Stop)")
            # We might enforce speed=0 here if strictly simulating ATP
            train["current_speed_limit"] = 0.0
            train["base_speed"] = 0.0
            # Clear other restrictions as this is absolute
            train["active_restrictions"] = []

            # 1. CTCS-2 (Temporary Speed Restriction)
        # Fields: Q_SCALE, V_TSR, D_TSR, L_TSR
        if "CTCS-2" in effective_balise:
            val = effective_balise["CTCS-2"]
            if val and isinstance(val, str) and len(val) > 8:
                try:
                    data = decode_packet("CTCS-2", val)
                    log_packets.append("CTCS-2")

                    q_scale = data.get("Q_SCALE", 1)
                    scale = PacketUtils.get_q_scale_factor(q_scale)

                    v_tsr = data.get("V_TSR", 0) * 5
                    d_tsr = data.get("D_TSR", 0)
                    l_tsr = data.get("L_TSR", 0)

                    start_km = b_loc + (d_tsr * scale / 1000.0)
                    end_km = start_km + (l_tsr * scale / 1000.0)

                    restr = {
                        "type": "CTCS-2",
                        "start_km": start_km,
                        "end_km": end_km,
                        "speed": float(v_tsr)
                    }
                    train["active_restrictions"].append(restr)
                except Exception:
                    pass

        # 2. ETCS-27 (Line Speed / Static Speed Profile)
        # Fields: Q_SCALE, V_STATIC, D_STATIC
        if "ETCS-27" in effective_balise:
            val = effective_balise["ETCS-27"]
            if val and isinstance(val, str) and len(val) > 8:
                try:
                    data = decode_packet("ETCS-27", val)
                    log_packets.append("ETCS-27")

                    v_static_code = data.get("V_STATIC", 127)
                    q_scale = data.get("Q_SCALE", 1)
                    scale = PacketUtils.get_q_scale_factor(q_scale)
                    d_static = data.get("D_STATIC", 0)

                    start_km = b_loc + (d_static * scale / 1000.0)

                    if v_static_code == 127:
                        # End of SSP? For now reset base speed to max
                        default_max = float(self.line_config.get("max_speed", 350.0))
                        train["base_speed"] = default_max
                    else:
                        speed_val = float(v_static_code * 5)
                        # ETCS-27 updates the Base Speed Profile
                        # It applies from start_km onwards (until changed)
                        # To handle delay (D_STATIC), we can treat it as a restriction with no end
                        # Or just update immediate base if D=0.
                        # For simplicity in this logic: Treat as restriction with None end?
                        # No, SSP is usually the "track speed".
                        # Let's say we update base_speed immediately if D=0.
                        # If D>0, we need a scheduled event.
                        # Simpler approach: Treat as restriction with no end, but prioritize min() logic.
                        # But wait, SSP should REPLACE base speed, not just cap it.
                        # If SSP goes 100 -> 200, min(old, new) keeps 100.
                        # So SSP must be the 'base'.
                        # Let's assume for this tester: ETCS-27 sets the base speed immediately (ignoring D_STATIC for base simple implementation)
                        # OR if user specifically tests D_STATIC:
                        if d_static == 0:
                            train["base_speed"] = speed_val
                        else:
                            # Schedule a base speed change? 
                            # Adding to active_restrictions works if we modify check_restrictions to distinguish "Base Updates" vs "Temporary Limits".
                            # Let's treat it as a "Temporary" limit that doesn't expire (End=None) for now,
                            # but that implies it only lowers speed.
                            # Proper ETCS logic is complex.
                            # User Requirement: "Limit speed exceeds valid distance... end speed limit" (CTCS-2 context).
                            # So for ETCS-27: Just set base speed.
                            train["base_speed"] = speed_val

                except Exception:
                    pass

        # Log event
        train_name = train.get("name", "Unknown Train")
        if log_packets:
            self.logger.log_balise_event(train_name, effective_balise)
        else:
            # Fallback for old manual config
            if "speed_limit" in effective_balise and str(effective_balise["speed_limit"]).strip():
                try:
                    limit = float(effective_balise.get("speed_limit"))
                    train["base_speed"] = limit
                    self.logger.log(f"Train {train_name} manual speed set to {limit}")
                except:
                    pass

    def zoom_in(self):
        """放大视图。关闭自动适应。"""
        self.auto_fit = False
        self.scale *= 1.2
        if self.scale > 1000000: self.scale = 1000000
        if self.follow_train_mode:
            self.update_follow_offset()
        self.update()

    def zoom_out(self):
        """缩小视图。关闭自动适应。"""
        self.auto_fit = False
        self.scale /= 1.2
        if self.scale < 0.0001: self.scale = 0.0001
        if self.follow_train_mode:
            self.update_follow_offset()
        self.update()

    def auto_fit_view(self):
        """自动调整视图以显示全线。"""
        self.auto_fit = True
        self.follow_train_mode = False
        self.update()

    def center_on_location(self, location, zoom_scale=5000.0):
        """
        聚焦视图到特定位置。
        
        参数:
            location (float): 线路位置 (km)。
            zoom_scale (float): 目标缩放比例。
        """
        self.auto_fit = False
        self.follow_train_mode = False

        # Set zoom level
        self.scale = zoom_scale
        if self.scale > 1000000: self.scale = 1000000

        # Calculate offset to center the location
        # screen_x = offset_x + location * scale
        # We want screen_x = width / 2
        # offset_x = width / 2 - location * scale
        center_screen_x = self.width() / 2
        self.offset_x = center_screen_x - float(location) * self.scale
        self.offset_y = self.height() / 2

        self.update()

    def keyPressEvent(self, event):
        """
        键盘事件处理。用于触发???（跳跃）。
        """
        if event.key() == Qt.Key_Up:
            for train in self.trains:
                name = train.get("name", "")
                if (
                        "JUMP" in name or "Jump" in name or "jump" in name
                ) and not train.get("is_jumping", False):
                    train["is_jumping"] = True
                    train["jump_v"] = 25.0  # Initial jump velocity
            # If simulation is paused, we need to manually trigger update to show jump frame-by-frame?
            # Or assume it only works when running.
            # Usually jump physics is in update_simulation which runs on timer.
            # If user wants to just jump while paused, it won't animate well.
            # But the requirement implies a game-like feel, so simulation running is expected.
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        """
        鼠标滚轮事件。处理 Ctrl+滚轮缩放。
        """
        if event.modifiers() & Qt.ControlModifier:
            self.auto_fit = False
            angle = event.angleDelta().y()
            factor = 1.1 if angle > 0 else 0.9

            # Calculate new scale
            new_scale = self.scale * factor
            if new_scale < 0.0001: new_scale = 0.0001
            if new_scale > 1000000: new_scale = 1000000

            if self.follow_train_mode:
                # If following, just update scale, offset will be fixed by update_follow_offset logic
                self.scale = new_scale
                self.update_follow_offset()
            else:
                # Adjust offset to zoom towards mouse position
                mouse_pos = event.position().x()
                # World coordinate under mouse before zoom
                world_x = (mouse_pos - self.offset_x) / self.scale

                self.scale = new_scale
                # New offset to keep world_x under mouse
                self.offset_x = mouse_pos - world_x * self.scale

            self.update()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """鼠标按下事件。处理左键拖拽应答器，右键平移。"""
        if event.button() == Qt.LeftButton:
            # Check hit for dragging
            click_pos = event.pos()
            triangle_h = 18
            triangle_w = 24

            for i, balise in enumerate(self.balises):
                loc = balise.get("location", 0)
                bx = self.offset_x + loc * self.scale
                by = self.offset_y

                # Hit detection (Triangle area)
                if abs(click_pos.x() - bx) <= triangle_w / 2 and \
                        0 <= (click_pos.y() - by) <= triangle_h:
                    self.is_dragging_balise = True
                    self.dragged_balise_index = i
                    self.drag_start_mouse_pos = click_pos
                    self.has_dragged = False
                    self.setCursor(Qt.SizeHorCursor)
                    return  # Consumed

        if event.button() == Qt.RightButton:
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.auto_fit = False
            self.follow_train_mode = False
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件。处理拖拽、平移和 Tooltip 显示。"""
        if self.is_dragging_balise:
            # Drag logic
            current_pos = event.pos()
            if not self.has_dragged:
                if (current_pos - self.drag_start_mouse_pos).manhattanLength() > 5:
                    self.has_dragged = True

            if self.has_dragged:
                # Calculate new location
                new_x = current_pos.x()
                new_loc = (new_x - self.offset_x) / self.scale

                # Clamp to track length
                if new_loc < 0: new_loc = 0
                if new_loc > self.track_length: new_loc = self.track_length

                # Update balise
                self.balises[self.dragged_balise_index]["location"] = float(f"{new_loc:.4f}")

                self.update()  # Repaint
            return

        if self.is_panning:
            delta = event.pos() - self.last_mouse_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()
            return

        # Tooltip logic
        mouse_pos = event.pos()
        min_dist = 20  # pixels
        hovered_balise = None

        # Reset hover state locally (will settle after loop)
        self.hovered_balise_index = -1
        self.cursor_global_pos = None

        for i, balise in enumerate(self.balises):
            loc = balise.get("location", 0)
            bx = loc * self.scale + self.offset_x
            by = self.offset_y

            dist = ((mouse_pos.x() - bx) ** 2 + (mouse_pos.y() - by) ** 2) ** 0.5
            if dist < min_dist:
                hovered_balise = balise
                self.hovered_balise_index = i
                self.cursor_global_pos = event.globalPosition().toPoint()
                break

        if hovered_balise:
            # Use effective packets for display to show current state (Red/Green)
            effective = self._get_effective_balise_packets(self.hovered_balise_index, self.current_sim_time)
            info = self.get_balise_tooltip_text(effective)

            # Force update on move to keep it following cursor
            QToolTip.showText(self.cursor_global_pos, info, self)
            self.last_tooltip_text = info
        else:
            QToolTip.hideText()
            self.last_tooltip_text = ""

        super().mouseMoveEvent(event)

    def get_balise_tooltip_text(self, balise):
        """
        获取应答器的提示文本（Tooltip）。
        用于在鼠标悬停时显示应答器的详细信息。
        
        Args:
            balise (dict): 应答器配置数据。
            
        Returns:
            str: 格式化后的HTML提示文本。包含基本信息、报文头详情以及解析后的用户信息包内容。
        """
        # Basic Info
        name = balise.get('name', 'Unknown')
        loc = balise.get('location', 0)
        b_type_val = str(balise.get('type', 0))
        b_type = "有源" if b_type_val == '1' else "无源"

        # Use HTML for better formatting
        lines = [
            f"<b>{name}</b> <span style='color:gray'>({b_type})</span>",
            f"位置: {loc} km"
        ]

        # Header Info
        nid_c = balise.get('nid_c', '0')
        nid_bg = balise.get('nid_bg', '0')
        lines.append(f"ID: <b>{nid_c}-{nid_bg}</b>")

        # Group Info & Translation
        father = balise.get('father_balise', '')
        sub_id = balise.get('sub_id', '0')
        n_pig = balise.get('n_pig', '000')
        n_total = balise.get('n_total', '1')

        # Translate binary N_PIG to int for display
        try:
            pig_int = int(str(n_pig), 2)
            pig_desc = f"{n_pig}({pig_int + 1})"
        except ValueError:
            pig_desc = str(n_pig)

        group_info = f"组内: {sub_id} (PIG:{pig_desc}/TOT:{n_total})"
        if father:
            group_info += f" [父: {father}]"
        lines.append(group_info)

        # Protocol Header Details
        m_ver = balise.get('m_version', '0010000')
        m_count = balise.get('m_mcount', '255')
        q_updown = balise.get('q_updown', '1')
        q_media = balise.get('q_media', '0')
        q_link = balise.get('q_link', '0')
        m_dup = balise.get('m_dup', '00')

        # Translations based on Balise.md/InfoPacket.md
        dir_str = "地->车" if str(q_updown) == '1' else "车->地"
        media_str = "环线" if str(q_media) == '1' else "应答器"
        link_str = "被链接" if str(q_link) == '1' else "未链接"

        dup_map = {"00": "无复制", "01": "复制后", "10": "复制前"}
        dup_str = dup_map.get(str(m_dup), str(m_dup))

        header_details = (
            f"V: {m_ver} | Cnt: {m_count} | {dup_str}<br>"
            f"{dir_str} | {media_str} | {link_str}"
        )
        lines.append(f"<span style='font-size:small; color:gray'>{header_details}</span>")

        # Packets
        packets_found = []
        for key, desc in PACKET_TYPE_MAP.items():
            val = balise.get(key, "")
            if val:
                # Try to decode if it looks like binary
                decoded_str = val
                if all(c in '01' for c in str(val)) and len(str(val)) > 8:
                    try:
                        decoded_data = decode_packet(key, str(val))
                        # Format decoded dict to string
                        items_str = []
                        if "Q_DIR" in decoded_data:
                            q_dir_desc = PacketUtils.get_q_dir_desc(PacketUtils.int_to_bin(decoded_data["Q_DIR"], 2))
                            items_str.append(f"Dir:{q_dir_desc}")
                        if "Q_SCALE" in decoded_data:
                            q_scale_desc = PacketUtils.get_q_scale_desc(
                                PacketUtils.int_to_bin(decoded_data["Q_SCALE"], 2))
                            items_str.append(f"Scale:{q_scale_desc}")

                        for k, v in decoded_data.items():
                            if k not in ["Q_DIR", "Q_SCALE"]:
                                items_str.append(f"{k}:{v}")
                        decoded_str = " ".join(items_str)
                    except Exception as e:
                        pass  # Fallback to raw value

                packets_found.append(f"<b>[{key}] {desc}</b>: {decoded_str}")

        if packets_found:
            lines.append("<hr><b>用户信息包:</b>")
            lines.extend(packets_found)

        return "<br>".join(lines)

    def mouseReleaseEvent(self, event):
        """
        处理鼠标释放事件。
        用于结束拖拽操作或触发点击事件。
        
        Args:
            event (QMouseEvent): 鼠标事件对象。
        """
        if event.button() == Qt.LeftButton:
            if self.is_dragging_balise:
                self.is_dragging_balise = False
                self.setCursor(Qt.ArrowCursor)

                if not self.has_dragged:
                    # It was a click, trigger edit
                    self.balise_edit_requested.emit(self.dragged_balise_index)
                else:
                    # It was a drag, notify parent of new location
                    new_loc = self.balises[self.dragged_balise_index].get("location", 0.0)
                    self.balise_moved.emit(self.dragged_balise_index, float(new_loc))

                self.dragged_balise_index = -1
                return

        if event.button() == Qt.RightButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        处理鼠标双击事件。
        在轨道附近双击左键可触发新建应答器信号。
        
        Args:
            event (QMouseEvent): 鼠标事件对象。
        """
        if event.button() == Qt.LeftButton:
            # Check if click is near the track Y position
            if abs(event.pos().y() - self.offset_y) < 30:  # 30 pixels tolerance
                # Calculate location
                click_x = event.pos().x()
                location = (click_x - self.offset_x) / self.scale

                # Check if location is within track bounds
                if 0 <= location <= self.track_length:
                    self.balise_create_requested.emit(location)

        super().mouseDoubleClickEvent(event)

    def paintEvent(self, event):
        """
        处理绘图事件。
        负责绘制背景、轨道、车站、应答器和列车。
        
        Args:
            event (QPaintEvent): 绘图事件对象。
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(50, 50, 50))

        # Auto fit logic
        if self.auto_fit:
            width = self.width() - 100  # Margin
            if self.track_length > 0:
                self.scale = width / self.track_length
            self.offset_x = 50
            self.offset_y = self.height() / 2

        # Draw track
        pen = QPen(Qt.white)
        pen.setWidth(2)
        painter.setPen(pen)

        start_x = self.offset_x
        end_x = self.offset_x + self.track_length * self.scale
        painter.drawLine(start_x, self.offset_y, end_x, self.offset_y)

        # Draw Stations
        painter.setPen(Qt.white)
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        for station in self.stations:
            loc = station.get("location", 0)
            x = self.offset_x + loc * self.scale
            y = self.offset_y
            # Draw tick
            painter.drawLine(x, y - 5, x, y + 5)
            # Draw name
            name = station.get("name", "Station")
            painter.drawText(int(x - 20), int(y + 45), name)

        # Draw Balises
        balise_groups = {}  # key -> list of (x_pos, balise_obj)

        for balise in self.balises:
            loc = balise.get("location", 0)
            try:
                b_type = int(balise.get("type", 0))
            except ValueError:
                b_type = 0

            x = self.offset_x + loc * self.scale
            y = self.offset_y

            # Grouping Logic
            father = str(balise.get("father_balise", "")).strip()
            name = str(balise.get("name", "")).strip()
            # If father is set, use it as key. Else use own name.
            # Note: This simply groups by the shared key.
            # If A is father, A has father="", key="A".
            # B has father="A", key="A".
            # Both go to "A".
            key = father if father else name
            if not key: key = "Unknown"

            if key not in balise_groups:
                balise_groups[key] = []
            balise_groups[key].append((x, balise))

            # Draw Triangle
            triangle_h = 18
            triangle_w = 24
            top_y = y  # Start directly from track line

            points = [
                QPointF(x, top_y),  # Top vertex
                QPointF(x - triangle_w / 2, top_y + triangle_h),  # Bottom Left
                QPointF(x + triangle_w / 2, top_y + triangle_h)  # Bottom Right
            ]

            if b_type == 1:
                # Active Balise: White Solid
                painter.setBrush(QColor(255, 255, 255))
                painter.setPen(Qt.NoPen)
                painter.drawPolygon(QPolygonF(points))
            else:
                # Passive Balise: Hollow (White Outline)
                painter.setBrush(Qt.NoBrush)
                pen = QPen(Qt.white)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPolygon(QPolygonF(points))

        # Draw Balise Labels (Groups)
        painter.setPen(Qt.white)
        font_label = QFont()
        font_label.setPointSize(8)
        painter.setFont(font_label)
        fm = painter.fontMetrics()

        for key, items in balise_groups.items():
            if not items: continue

            # Calculate visual center of the group
            xs = [item[0] for item in items]
            min_x = min(xs)
            max_x = max(xs)
            center_x = (min_x + max_x) / 2

            # Determine text
            if len(items) > 1:
                label = key
            else:
                # Single balise, use its own name
                label = items[0][1].get("name", "")

            if not label: continue

            text_w = fm.horizontalAdvance(label)
            # Y position: Track Y + Triangle Height + Margin
            text_y = self.offset_y + 18 + 12

            painter.drawText(int(center_x - text_w / 2), int(text_y), label)

        # Draw Trains
        for train in self.trains:
            loc = train.get("current_location", 0)
            x = self.offset_x + loc * self.scale

            # Apply jump offset
            jump_h = train.get("jump_h", 0.0)
            y = self.offset_y - jump_h

            if not self.train_img.isNull():
                scale_factor = 0.06
                w = self.train_img.width() * scale_factor
                h = self.train_img.height() * scale_factor
                painter.drawPixmap(QRect(int(x - w / 2), int(y - h - 5), int(w), int(h)), self.train_img)
            else:
                painter.setBrush(Qt.red)
                painter.drawRect(x - 10, y - 20, 20, 10)
