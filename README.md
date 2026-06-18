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

## Installation

1. Clone the repository
2. Install dependencies: `pip install PyQt5` or `pip install PyQt6`
3. Run the application: `python main.py`

## Usage

### Main Menu Tab
- Select AC content root directory to enable content discovery
- Manage server folders using the CRUD operations (Add, Duplicate, Rename, Delete)
- Create new servers from the VS Server template

### Server Configuration Tab
- Edit server information including name and track selection
- Configure network ports (UDP, TCP, HTTP)
- Set time of day settings
- Manage entry list with car/skin selection for each driver
- Double-click on car or skin columns to open selection dialogs

### Virtual Steward Tab
- Configure replay file handling for Virtual Steward plugin
- Set bot train parameters including gap distance and number of bots
- Enable/disable Patreon support features

## Project Structure

```
.
├── main_menu_tab.py          # Main menu and server management
├── server_config_tab.py      # Server configuration editing
├── virtual_steward_tab.py    # Virtual Steward plugin configuration
├── file_manager.py           # File operations and content discovery
├── widgets/                  # Custom Qt widgets
│   └── entry_list_table.py   # Entry list table with drag-and-drop support
├── dialogs/                  # Dialog windows for selection
│   ├── car_selection_dialog.py
│   ├── skin_selection_dialog.py
│   └── track_selection_dialog.py
└── VS Server/                # Template server directory (not included in repo)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Support

For support, please open an issue on the GitHub repository or contact the project maintainers.