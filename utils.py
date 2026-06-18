"""
Utility functions for the Assetto Corsa Server Configuration Manager
"""

import sys
from pathlib import Path


def get_resource_path(relative_path):
    """
    Get the absolute path to a bundled resource.
    Handles both PyInstaller bundles and source execution.
    """
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS) / relative_path
    else:
        # Running from source
        return Path(__file__).parent / relative_path


def format_display_string(s):
    """
    Convert a config string to display format.
    Replaces underscores with spaces and converts to uppercase.
    
    Example: "nissan_skyline_r32" -> "NISSAN SKYLINE R32"
    """
    if not s:
        return ""
    return s.replace('_', ' ').upper()
