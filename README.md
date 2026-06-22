# Assetto Corsa Server Configuration Manager

A comprehensive GUI application for managing Assetto Corsa server configurations with support for Virtual Steward plugin integration.

## Features

- **Server Management**: Create, duplicate, rename, and delete server directories
- **Template System**: Copy from VS Server template to create new servers
- **Content Discovery**: Automatic detection of tracks, cars, and skins from AC content root
- **Server Configuration**: Edit server information including name, track, ports, and time settings
- **Entry List Management**: Configure driver entries with car and skin selection
- **Virtual Steward Integration**: Replay file handling and bot configuration
- **Drag-and-Drop Reordering**: Rearrange entry list items in the configuration table

## Requirements

- Python 3.6+
- PyQt5 or PyQt6
- Assetto Corsa content files (tracks, cars, skins, weather)
- VS Server folder: A `VS Server` folder must be present in the same directory as the executable. This folder serves as a template that gets copied when creating new servers using the "Add Server" button.

## Installation

1. Clone the repository
2. Install dependencies: `pip install PyQt5` or `pip install PyQt6`
3. Run the application: `python main.py`

## Project Structure

```
.
├── main_menu_tab.py          # Main menu and server management with integrated terminal
├── server_config_tab.py      # Server configuration editing including entry list management
├── virtual_steward_tab.py    # Virtual Steward plugin configuration and bot training settings
├── file_manager.py           # File operations and content discovery utilities
├── widgets/                  # Custom Qt widgets
│   └── entry_list_table.py   # Entry list table with drag-and-drop reordering support
├── dialogs/                  # Dialog windows for selection (car, skin, track)
│   ├── car_selection_dialog.py
│   ├── skin_selection_dialog.py
│   └── track_selection_dialog.py
└── VS Server/                # Template server directory (not included in repo)
```

## How to Use the Built Application

###### Note: VS Server Folder and ACServerManager must be in the same directory. VS Server is template server for "Add Server" button.

1. **Launch the Application**: Run `main.py` or the compiled executable

2. **Configure Content Root**:
   - Set the AC Content Root path to your Assetto Corsa installation directory
   - This enables automatic discovery of tracks, cars, and skins

3. **Manage Servers**:
   - Set the Server Folder path to where you want to store server configurations
   - Use CRUD operations (Add, Duplicate, Rename, Delete) to manage servers
   - Create new servers from the VS Server template

4. **Configure Server Settings**:
   - Select a server from the list
   - Edit server information in the Server Configuration tab
   - Configure entry list with driver entries and car/skin selection
   - Set Virtual Steward plugin options in the Virtual Steward tab

5. **Save Changes**:
   - All changes are automatically tracked for unsaved modifications
   - Click "Save Changes" or close the application to persist configurations
   - The application will prompt to save before closing if there are unsaved changes

6. **Start Servers**:
   - Select a server from the list
   - Click "Start Server" to launch it
   - Monitor output in the integrated terminal window

## Detailed Field Descriptions

### Main Menu Tab
- **AC Content Root**: Path to your Assetto Corsa installation directory for content discovery
- **Server Folder (parent dir)**: Directory containing all server configurations
- **Add Server**: Create a new server from the VS Server template
- **Duplicate Server**: Create a copy of an existing server configuration
- **Rename Server**: Change the name of a selected server
- **Delete Server**: Remove selected servers (cannot be undone)
- **Start Server**: Launch the currently selected server
- **Stop Server**: Terminate the currently running server

### Server Configuration Tab
- **Server Name**: Display name for your server in the lobby
- **Track**: Track to use for races (double-click to select from available tracks)
- **UDP Port**: Network port for UDP communication (default 9600)
- **TCP Port**: Network port for TCP communication (default 9601)
- **HTTP Port**: Network port for HTTP web interface (default 8080)
- **Time of Day (Dynamic)**: Enable dynamic time progression
- **Time**: Time of day setting when dynamic time is disabled
- **Server Description**: Text description displayed to players in the lobby

### Entry List Tab
- **Model**: Car model for this entry (double-click to select from available cars)
- **Skin**: Car skin for this entry (double-click to select from available skins)
- **Preview**: Visual preview of the car skin
- **Add Entry**: Add a new driver entry to the list
- **Remove Entry**: Delete selected entries from the list
- **Duplicate Entry**: Create a copy of the selected entry

### Virtual Steward Tab
- **Enable Virtual Steward Replay Plugin**: Activate the Virtual Steward plugin features
- **Select Replay File**: Choose an .acreplay file for replay functionality
- **Loop Lap**: Number of laps to loop the replay (leave empty for full race)
- **Enable Bot Trains**: Enable automatic bot training with replay files
- **Train Gap (frames)**: Time gap between bots in frames (5-100)
- **Number of Bots**: Total number of bots to create from the replay

### Advanced Options Tab
- **Weather**: Select weather conditions for races
- **Force Headlights**: Enable headlights even during daytime
- **Allowed Tyres Out**: Number of tyres allowed out of pit lane (0-4)
- **Loading Image Url**: URL for loading screen image
- **Client Send Interval HZ**: Network update frequency (default 33)
- **Player Loading Timeout Minutes**: Time to wait for player connection (default 10)
- **Admins**: List of admin Steam IDs with server access
- **Blacklist**: List of banned Steam IDs
- **Whitelist**: List of allowed Steam IDs

## Features

- **Server Management**: Create, duplicate, rename, and delete server directories
- **Template System**: Copy from VS Server template to create new servers
- **Content Discovery**: Automatic detection of tracks, cars, and skins from AC content root
- **Server Configuration**: Edit server information including name, track, ports, and time settings
- **Entry List Management**: Configure driver entries with car and skin selection
- **Virtual Steward Integration**: Replay file handling and bot configuration
- **Drag-and-Drop Reordering**: Rearrange entry list items in the configuration table
- **Integrated Terminal**: Real-time monitoring of server output
- **Change Tracking**: Automatic detection of unsaved changes

## License

### Assetto Corsa Server Configuration Manager

This project is licensed under the MIT License.

See the [LICENSE](./LICENSE) file for full details.

---

### Third-Party Software

This application distributes **AssettoServer**, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

AssettoServer Copyright:
Copyright (C) 2025 Niewiarowski, compujuckel

AssettoServer is distributed under its own license terms. The AGPL-3.0 license requires that its source code and license text be made available to users.

The full license text and notices are included in:

- `THIRD_PARTY/AssettoServer/LICENSE`
- `THIRD_PARTY/AssettoServer/NOTICE`

AssettoServer source code is available from its official repository.

---

### Disclaimer

Assetto Corsa Server Configuration Manager is an independent project and is not affiliated with or endorsed by Kunos Simulazioni or the AssettoServer developers.
## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Support

For support, please open an issue on the GitHub repository or contact the project maintainers.
