# Refactored Application Structure - Module Guide

This guide documents the refactored architecture of the Assetto Corsa Server Configuration Manager. The original monolithic `main.py` has been split into organized, modular files that are easier to maintain, extend, and test.

## Architecture Overview

The refactored application uses a modular architecture where:
- **Utility modules** handle generic functions
- **Component modules** (widgets, dialogs) handle UI elements
- **Feature modules** handle specific functionality
- **Main2.py** orchestrates everything in the `ACServerConfigGUI` main window

```
main2.py                      # Main application window and orchestration
├── utils.py                  # Utility functions
├── widgets.py                # Custom PyQt5 widgets
├── dialogs.py                # Custom dialog windows
├── file_manager.py           # File and folder operations
├── config_manager.py         # INI/YAML config file handling
├── main_menu_tab.py          # Main Menu tab functionality
├── server_config_tab.py      # Server Configuration tab
├── virtual_steward_tab.py    # Virtual Steward tab
└── advanced_options_tab.py   # Advanced Options tab
```

## Module Descriptions

### **utils.py** - Utility Functions
Contains generic helper functions used across the application.

**Key Functions:**
- `get_resource_path(relative_path)` - Resolves bundled resource paths
- `format_display_string(s)` - Converts underscore-separated strings to formatted display text

**Why separate?** These utilities are commonly used and can be easily reused or unit tested independently.

---

### **widgets.py** - Custom PyQt5 Widgets
Contains custom widget classes that extend PyQt5 functionality.

**Classes:**
- `PathLineEdit` - QLineEdit that emits signal when focus is lost
- `ClickableLineEdit` - QLineEdit that signals on double-click
- `EntryListTable` - Custom QTableWidget with drag-and-drop row reordering and auto-scroll

**Why separate?** These reusable widgets can be used in other parts of the app and are independent of business logic.

---

### **dialogs.py** - Custom Dialogs
Contains all dialog window classes for selecting cars, skins, and tracks.

**Classes:**
- `CarSelectionDialog` - Dialog for selecting cars with search functionality
- `SkinSelectionDialog` - Dialog for selecting car skins with preview images
- `TrackSelectionDialog` - Dialog for selecting tracks with search

**Why separate?** Dialogs are self-contained UI components that can be easily modified or reused.

---

### **file_manager.py** - File & Folder Operations
Handles all file system operations: discovering resources, managing server folders, and reading/writing files.

**Key Functions:**
- `discover_tracks(content_root)` - Find available tracks
- `discover_cars(content_root)` - Find available cars
- `discover_weather(content_root)` - Find available weather
- `get_car_skins(content_root, car_name)` - Get skins for a car
- `list_server_directories(servers_parent_dir)` - List all servers
- `copy_server_template(servers_parent_dir)` - Add new server from template
- `duplicate_server(src_path, servers_parent_dir)` - Duplicate a server
- `rename_server_folder(old_path, new_name)` - Rename server folder
- `delete_server_folders(folder_paths)` - Delete servers
- `read_text_file(file_path)` - Read lines from file
- `write_text_file(file_path, lines)` - Write lines to file
- `get_unique_folder_name(parent, base_name)` - Generate unique folder names

**Why separate?** All file operations are isolated, making it easy to:
- Add caching or performance optimizations
- Handle errors consistently
- Test file operations independently
- Mock file operations in unit tests

---

### **config_manager.py** - Configuration File Handling
Handles loading and saving of INI and YAML configuration files with targeted updates.

**Key Functions:**
- `load_configs(server_root)` - Load all config files from server
- `save_ini_targeted(path, section_updates)` - Update specific INI keys
- `save_yaml_targeted(path, scalar_updates, enable_plugins)` - Update specific YAML keys
- `write_entry_list_ini(path, entry_list_data)` - Write entry_list.ini
- `update_data_track_params(path, track_value)` - Update track params
- `folder_exists(path)` / `file_exists(path)` - Check existence

**Why separate?** Configuration handling is complex with multiple file formats:
- INI files (server_cfg.ini, entry_list.ini, data_track_params.ini)
- YAML files (extra_cfg.yml, plugin_vs_replay_cfg.yml)
- Text files (admins.txt, blacklist.txt)

Separating this allows targeted, in-place updates that preserve formatting and comments.

---

### **main_menu_tab.py** - Main Menu Tab
Contains the `MainMenuTab` widget that handles folder selection and server management.

**Key Features:**
- AC Content Root folder selection and path validation
- Server folder (parent) selection
- Server list display with dynamic updates
- Server management: Add, Duplicate, Rename, Delete
- Settings persistence

**UI Components:**
- Folder selection inputs with Browse buttons
- Server list widget
- Server management buttons

**Event Handlers:**
- `on_content_path_edited()` - Handle manual path entry
- `on_server_path_edited()` - Handle server folder path entry
- `on_server_list_item_clicked()` - Load selected server
- `add_server()` / `duplicate_server()` / `rename_server()` / `delete_server_folder()`

**Why separate?** The Main Menu has distinct responsibilities:
- Folder/path management
- Server CRUD operations
- List population and filtering

Separating it makes these operations easy to modify and test.

---

### **server_config_tab.py** - Server Configuration Tab
Contains the `ServerConfigTab` widget with server configuration fields and entry list management.

**Key Features:**
- Server information editing (name, track, ports)
- Time of day settings
- Server description
- Entry list (car/skin selection with drag-and-drop reordering)

**UI Components:**
- Server config form (name, track, ports, time)
- Server description text editor
- Entry list table with preview images
- Entry list buttons (Add, Remove, Duplicate)

**Key Methods:**
- `on_entry_double_clicked()` - Open car/skin dialogs on cell click
- `on_entry_selection_changed()` - Update button states

**Why separate?** The Server Configuration tab contains:
- Complex form handling
- Entry list management with drag-and-drop
- Integration with car/track/skin selection dialogs

Separating it keeps this complexity organized and testable.

---

### **virtual_steward_tab.py** - Virtual Steward Tab
Contains the `VirtualStewardTab` widget for Virtual Steward plugin configuration.

**Key Features:**
- VS plugin enable/disable
- Replay file management (add/select replay files)
- Bot trains configuration with slider
- Number of bots selection
- Loop lap input

**UI Components:**
- VS checkbox
- Replay file button
- Lap number input
- Bot trains checkbox and gap slider
- Number of bots combo
- Support/Patreon links

**Key Methods:**
- `on_add_replay_file_clicked()` - File dialog for replay files

**Why separate?** Virtual Steward is a distinct feature area:
- Has its own configuration file (plugin_vs_replay_cfg.yml)
- Has specific UI controls (slider, file picker)
- Can be enabled/disabled independently

Separating it makes the feature self-contained and easy to modify.

---

### **advanced_options_tab.py** - Advanced Options Tab
Contains the `AdvancedOptionsTab` widget for advanced server settings.

**Key Features:**
- Weather selection
- Force headlights option
- Tires allowed out setting
- Custom loading screen URL
- Client send interval HZ
- Player loading timeout
- Admin list management (add/remove)
- Blacklist management (add/remove)
- Server logs access (crash logs, server logs, server folder)

**UI Components:**
- Weather dropdown
- Headlights checkbox
- Tires dropdown
- URL input
- Interval/timeout inputs
- Admin/Blacklist lists with add/remove buttons
- Log access buttons

**Key Methods:**
- `open_add_admin_dialog()` / `open_add_blacklist_dialog()` - Add dialogs
- `remove_admin()` / `remove_blacklist()` - Remove entries
- `open_crash_logs_folder()` / `open_server_logs_folder()` - Open Explorer windows

**Why separate?** Advanced Options is a collection of miscellaneous settings:
- Different configuration sources (server_cfg.ini, extra_cfg.yml, .txt files)
- List management (admins, blacklist)
- File system access (log folders)

Separating it keeps these diverse features organized.

---

### **main2.py** - Main Application Window
The orchestrator that ties everything together. Contains the main `ACServerConfigGUI` class (the main window).

**Key Responsibilities:**
- Create and manage all tabs
- Load/save settings
- Load/populate config files
- Coordinate data flow between tabs
- Handle app-level actions (launch server, close app)

**Key Methods:**
- `create_left_tabbed_panel()` - Create all tabs
- `auto_load_configs()` - Load configs from selected server
- `populate_all_fields()` - Sync all widgets from config data
- `populate_server_config()` - Populate Server Config tab fields
- `populate_entry_list()` - Parse and display entry list
- `populate_server_description()` - Load VS settings
- `populate_bot_trains_config()` - Load bot configuration
- `populate_advanced_options()` - Populate Advanced Options tab
- `save_config()` - Save all config changes to files
- `refresh_entry_list_table()` - Update entry list display
- `on_add_entry()` / `on_remove_entry()` / `on_duplicate_entry()` - Entry management
- `on_entry_list_reordered()` - Handle drag-and-drop reordering
- `on_num_bots_changed()` - Handle bot count changes
- `on_vs_enabled_changed()` - Enable/disable VS controls
- `launch_server()` - Launch the server executable
- `closeEvent()` - Handle app close with unsaved changes warning

**Why separate?** Main2.py serves as the application orchestrator:
- Keeps logic that depends on multiple tabs here
- Handles cross-tab coordination
- Manages settings and configuration lifecycle
- Provides app-level functionality (launch, close)

---

## Data Flow

### Loading Configurations

```
User selects server folder
    ↓
main_menu_tab.on_server_list_item_clicked()
    ↓
main2.auto_load_configs()
    ↓
config_manager.load_configs()
    ↓
parse INI/YAML files → self.configs dict
    ↓
main2.populate_all_fields()
    ↓
main2.populate_server_config()
main2.populate_entry_list()
main2.populate_server_description()
main2.populate_bot_trains_config()
main2.populate_advanced_options()
    ↓
All tabs display loaded configuration
```

### Saving Configurations

```
User changes settings
    ↓
mark_as_modified() flag set
    ↓
User clicks "Save Changes" or closes app
    ↓
main2.save_config()
    ↓
Gather data from all tab widgets
    ↓
config_manager.save_*_targeted()
    ↓
INI/YAML files updated with changes
```

### Adding/Removing Entries

```
User clicks "Add Entry"
    ↓
main2.on_add_entry()
    ↓
dialogs.CarSelectionDialog shows
    ↓
User selects car → get available skins
    ↓
main2.add_entry_to_list()
    ↓
entry_list_data appended
    ↓
main2.refresh_entry_list_table()
    ↓
server_config_tab.entry_list_table updated
```

---

## Adding New Functionality

### To add a new tab:

1. **Create new tab file** (e.g., `my_tab.py`):
   ```python
   class MyTab(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.parent_window = parent
           self.init_ui()
       
       def init_ui(self):
           # Build UI
           pass
   ```

2. **Register in main2.py**:
   ```python
   def create_left_tabbed_panel(self):
       self.my_tab = MyTab(self)
       tab_widget.addTab(self.my_tab, "My Tab")
   ```

3. **Add populate method in main2.py**:
   ```python
   def populate_my_tab(self, config_data):
       # Load data into my_tab widgets
       pass
   ```

4. **Add save logic in main2.py's save_config()**:
   ```python
   # Save my_tab changes
   scalar_updates = {}
   # ... gather changes from my_tab widgets
   config_manager.save_yaml_targeted(config_path, scalar_updates)
   ```

### To add new file operations:

1. Add function to `file_manager.py`
2. Import in `main2.py` or relevant tab file
3. Use in appropriate place

### To add new config handling:

1. Add loading logic to `config_manager.load_configs()`
2. Add save logic to `config_manager.save_*_targeted()`
3. Add populate method in `main2.py`
4. Add save logic in `main2.py.save_config()`

---

## Testing & Maintenance

### Benefits of Modular Structure

✅ **Easier Testing**
- Each module can be unit tested independently
- Mock file operations in `file_manager.py` tests
- Test dialogs independently in `dialogs.py`

✅ **Easier Modification**
- Add new tab without touching existing tabs
- Modify tab UI without affecting others
- Change file handling without affecting UI

✅ **Easier Debugging**
- Issues are localized to specific modules
- Follow data flow through specific imports
- Use print/logging at module boundaries

✅ **Code Reuse**
- Widgets can be used in multiple places
- Utility functions are reusable
- Config operations are centralized

✅ **Performance**
- Can add caching in `file_manager.py`
- Can add progress dialogs in `main2.py`
- Can lazy-load tabs

---

## Migration from main.py

**Do not modify main.py** - it's kept as-is for reference.

Use **main2.py** as the primary entry point:
```bash
python main2.py
```

Or update build configuration to use main2.py:
```python
# In ACServerConfigManager.spec
a = Analysis(['main2.py'], ...)
```

---

## File Structure Summary

| File | Lines | Purpose |
|------|-------|---------|
| utils.py | ~30 | Generic utilities |
| widgets.py | ~110 | Custom widgets |
| dialogs.py | ~280 | Selection dialogs |
| file_manager.py | ~180 | File operations |
| config_manager.py | ~220 | Config file handling |
| main_menu_tab.py | ~290 | Server management |
| server_config_tab.py | ~260 | Server config editing |
| virtual_steward_tab.py | ~140 | VS plugin config |
| advanced_options_tab.py | ~360 | Advanced settings |
| **main2.py** | **~900** | **Main orchestrator** |
| **Total (excluding main.py)** | **~2,770** | **Same as original** |

---

## Architecture Principles

1. **Separation of Concerns** - Each module has a single, clear responsibility
2. **Modularity** - Components are independent and can be developed/tested separately
3. **DRY (Don't Repeat Yourself)** - Common functionality extracted to utilities and managers
4. **Testability** - Each module can be tested in isolation
5. **Maintainability** - Related functionality is grouped together
6. **Extensibility** - New tabs and features can be added without modifying existing code

---

## Next Steps

To further improve the codebase:

1. **Add unit tests** for each module
2. **Add type hints** for better IDE support
3. **Add logging** for debugging
4. **Add configuration presets** feature
5. **Add undo/redo** functionality
6. **Add validation** for config values
7. **Add backup** before saving configs
8. **Add themes** for UI customization
