#!/usr/bin/env python3
"""
Build script for creating executable from Assetto Corsa Server Configuration Manager
"""

import os
import sys
import subprocess
from pathlib import Path

def create_build_script():
    """Create a build script for PyInstaller"""
    
    build_script = '''#!/usr/bin/env python3
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

# Build the executable
build_args = [
    'pyinstaller',
    '--name', 'ACServerManager',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconsole',
    '--icon=app_icon.ico' if os.path.exists('app_icon.ico') else '',
    'main.py'
]

try:
    subprocess.check_call(build_args)
    print("Build completed successfully!")
    print("Executable created in the 'dist' folder")
except subprocess.CalledProcessError as e:
    print(f"Build failed with error: {e}")
    sys.exit(1)
'''

    with open('build_exe.py', 'w') as f:
        f.write(build_script)
    
    # Make it executable
    os.chmod('build_exe.py', 0o755)

def main():
    """Main build function"""
    print("Creating build script for Assetto Corsa Server Manager...")
    
    try:
        # Check if main.py exists
        if not os.path.exists('main.py'):
            print("Error: main.py not found in current directory")
            return False
            
        create_build_script()
        print("Build script 'build_exe.py' created successfully!")
        print("\nTo build the executable:")
        print("1. Install PyInstaller: pip install pyinstaller")
        print("2. Run: python build_exe.py")
        return True
        
    except Exception as e:
        print(f"Error creating build script: {e}")
        return False

if __name__ == "__main__":
    main()