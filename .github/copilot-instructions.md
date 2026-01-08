# Balise Tester AI Instructions

You are working on **Balise Tester**, a PySide6-based visualization and simulation tool for railway balises and train operations.

## Project Architecture

### Core Components
- **Entry Point**: `main.py` initializes the `QApplication` and `MainWindow`.
- **Main Logic**: `balise_tester/main_window.py` (`MainWindow`) acts as the central controller, managing data loading, UI initialization, and signal wiring.
- **Simulation Loop**: `balise_tester/widgets/simulation_widget.py` contains the core `SimulationWidget`.
  - Uses `QTimer` (~16ms/60FPS) for the simulation loop.
  - Handles custom painting (`paintEvent`) with `QPainter`.
  - Manages internal state (`trains`, `balises`) separate from the file config until saved.
- **Data Management**: `balise_tester/core/config_manager.py` handles loading/saving JSON and CSV files.
  - **Critical**: Handles path resolution for both development and PyInstaller frozen builds (`sys.frozen`).

### UI Structure
- **Design Files**: UI layouts are defined in `ui/*.ui` (Qt Designer files).
- **Generated Code**: Python files in `ui/` (e.g., `ui/main.py`) are generated from `.ui` files.
  - **Rule**: NEVER edit `ui/*.py` files directly. Changes will be overwritten.
  - Implement logic in the corresponding wrapper classes in `balise_tester/windows/` or `balise_tester/dialogs/`.

### Directory Layout
- `balise_tester/`: Source code package.
  - `core/`: Logic helpers (Config, Logger, Packet Utils).
  - `widgets/`: Custom UI widgets (SimulationView).
  - `dialogs/` & `windows/`: Application windows and config dialogs.
- `data/config/`: Runtime configuration files (`balises.csv`, `stations.json`, etc.).
- `assets/`: Static resources (images).

## Development Workflows

### Running the Application
```bash
python main.py
```

### Building the Executable
Use `build_exe.bat` to create a standalone executable via PyInstaller.
- Ensure `assets/` and `data/` are correctly bundled (handled by `--add-data` in the script).

### Configuration
Data is persisted in `data/config/`. The application loads these into memory on startup and saves them back when explicitly requested via the UI ("Save Config").

## Coding Conventions

- **Qt Framework**: Use **PySide6**. Prefer new-style Signal/Slot syntax (`signal.connect(slot)`).
- **Simulation Coordinate System**:
  - `SimulationWidget` manages its own coordinate system (km -> pixels) via `self.scale` and `self.offset_x/y`.
  - Always transform coordinates when handling mouse events in the simulation view.
- **Path Handling**:
  - Use `os.path.join` and relative paths from `__file__` or `sys._MEIPASS` (for frozen builds).
  - Refer to `ConfigManager.__init__` for the canonical path resolution pattern.
- **Data Flow**:
  - UI Actions -> `MainWindow` -> `SimulationWidget` updates.
  - Signals (`trains_updated`, `balise_moved`) propagate changes back to the UI/Data model.

## Common Tasks

- **Adding a new Config Type**:
  1. Add load/save logic in `ConfigManager`.
  2. Add data structure in `MainWindow`.
  3. Pass data to `SimulationWidget`.
- **Modifying Simulation Logic**:
  - Edit `SimulationWidget.update_simulation` for per-tick logic.
  - Ensure thread safety if introducing new threads (currently single-threaded QTimer).
- **Customizing Appearance**:
  - Edit `paintEvent` in `SimulationWidget` for map rendering.
  - Update `Matplotlib` code in `windows/map_scheduler_window.py` for charts.
