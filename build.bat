@echo off
echo Building Assetto Corsa Server Configuration Manager executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.6 or higher.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Error installing PyInstaller
        pause
        exit /b 1
    )
)

REM Build the executable
echo Building executable...
python -m PyInstaller ^
--name ACServerManager ^
--onefile ^
--windowed ^
--clean ^
--noconsole ^
--icon=app_icon.ico ^
main.py

if %errorlevel% equ 0 (
    echo.
    echo Build completed successfully!
    echo Executable created in the 'dist' folder
) else (
    echo.
    echo Build failed!
)

pause