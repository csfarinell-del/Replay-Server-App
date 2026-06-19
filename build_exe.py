#!/usr/bin/env python3
import os
import sys
import subprocess

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("Building Assetto Corsa Server Configuration Manager executable...")

# Check if PyInstaller is installed
try:
    import PyInstaller
except ImportError:
    print("PyInstaller not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# Build the executable with icon
build_args = [
    'pyinstaller',
    '--name', 'ACServerManager',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconsole',
    '--icon=app_icon.ico',
    'main.py'
]

try:
    subprocess.check_call(build_args)
    print("Build completed successfully!")
    print("Executable created in the 'dist' folder")
except subprocess.CalledProcessError as e:
    print(f"Build failed with error: {e}")
    sys.exit(1)
