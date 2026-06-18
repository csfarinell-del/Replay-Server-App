# Building Assetto Corsa Server Configuration Manager

## Prerequisites

- Python 3.6 or higher
- PyQt5 or PyQt6 installed
- PyInstaller (for creating executables)

## Installation

```bash
pip install PyQt5
# or
pip install PyQt6
```

## Running the Application

```bash
python main.py
```

## Building Executable

### Method 1: Using Provided Scripts

#### Windows
Run the provided batch file:
```cmd
build.bat
```

#### Linux/Mac
Make executable and run:
```bash
chmod +x build.sh
./build.sh
```

### Method 2: Manual PyInstaller Command

```bash
pyinstaller --onefile --windowed --name ACServerManager main.py
```

### Method 3: Using setup.py

```bash
python setup.py bdist_wheel
```

## Build Requirements

The application requires the following Python packages:
- PyQt5 or PyQt6 (GUI framework)
- Standard library modules (pathlib, os, sys, etc.)

## Output Location

After building, the executable will be located in the `dist` folder.

## Troubleshooting

### Common Issues
1. **Missing PyQt**: Install with `pip install PyQt5`
2. **PyInstaller not found**: Install with `pip install pyinstaller`
3. **Icon not found**: The build script looks for `app_icon.ico` in the root directory

### Build Process
The build process will:
1. Create a single executable file
2. Include all necessary Python dependencies
3. Package the application as a portable executable
4. Generate output in the `dist` folder

## Notes

- The application uses relative paths and should work when deployed with its supporting files
- For best results, ensure all dependencies are installed before building
- The build scripts include error handling for common issues