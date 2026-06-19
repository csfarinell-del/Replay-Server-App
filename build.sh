#!/bin/bash

echo "Building Assetto Corsa Server Configuration Manager executable..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.6 or higher."
    exit 1
fi

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "Error installing PyInstaller"
        exit 1
    fi
fi

# Build the executable
echo "Building executable..."
python3 -m PyInstaller \
--name ACServerManager \
--onefile \
--windowed \
--clean \
--noconsole \
--icon=app_icon.ico \
--add-data="app_icon.ico:." \
--add-data="files/Icon.png:files" \
main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Build completed successfully!"
    echo "Executable created in the 'dist' folder"
else
    echo ""
    echo "Build failed!"
fi
