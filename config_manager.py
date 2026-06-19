"""
Configuration file management for the Assetto Corsa Server Configuration Manager

This module provides high-level I/O operations for server configuration files.
It abstracts the details of INI and YAML parsing, allowing callers to work with
Python dicts while maintaining the underlying file structure.

Configuration Files (located in server_root/cfg/):
1. server_cfg.ini
   - [SERVER]: NAME, TRACK, UDP_PORT, TCP_PORT, HTTP_PORT, TIME_OF_DAY_MULT, SUN_ANGLE, MAX_CLIENTS, ALLOWED_TYRES_OUT, CLIENT_SEND_INTERVAL_HZ
   - [WEATHER_0]: GRAPHICS (weather name)
   - Additional sections for advanced server settings

2. entry_list.ini
   - [CARS]: List of player and bot car entries
   - Each entry has: MODEL (car name), SKIN, DRIVERNAME, TEAM, SPECTATOR_MODE, GUID, BALLAST, RESTRICTOR

3. extra_cfg.yml
   - ServerDescription: Human-readable server info
   - EnablePlugins: List of enabled plugin names (e.g., 'VSReplayPlugin')

4. plugin_vs_replay_cfg.yml
   - AutoStartOffset: Indicates bot train mode if != 0
   - AutoStartStagger: Gap between bots in train
   - LoopLap: Number of laps to repeat for replay

Key Mappings for Virtual Steward:
- Bot entries have GUID = "8888880 + index" (non-bot entries have empty GUID)
- Bot skins have '/VS' suffix appended to differentiate from player skins
- EnablePlugins must contain 'VSReplayPlugin' for Virtual Steward to function

Important Note on data_track_params.ini:
- This file contains reference track configurations and should NOT be modified
- It's auto-generated based on the AC content root
- The track selection in server_cfg.ini is independent of this file
"""

import configparser
from pathlib import Path
from typing import Dict, List, Any, Optional


try:
    import yaml
except ImportError:
    yaml = None


def load_configs(server_root: str) -> Dict[str, Any]:
    """
    Load all configuration files from a server directory.
    
    Args:
        server_root: Path to server root directory
    
    Returns:
        Dictionary containing loaded configs
    """
    configs = {}
    cfg_path = Path(server_root) / "cfg"
    
    # Load server_cfg.ini
    server_cfg_path = cfg_path / "server_cfg.ini"
    if server_cfg_path.exists():
        parser = configparser.ConfigParser()
        parser.read(str(server_cfg_path))
        configs['server_cfg.ini'] = {
            'path': str(server_cfg_path),
            'parser': parser
        }
    
    # Load entry_list.ini
    entry_list_path = cfg_path / "entry_list.ini"
    if entry_list_path.exists():
        parser = configparser.ConfigParser()
        parser.read(str(entry_list_path))
        configs['entry_list.ini'] = {
            'path': str(entry_list_path),
            'parser': parser
        }
    
    # Load extra_cfg.yml
    extra_cfg_path = cfg_path / "extra_cfg.yml"
    if extra_cfg_path.exists():
        try:
            with open(str(extra_cfg_path), 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            configs['extra_cfg.yml'] = {
                'path': str(extra_cfg_path),
                'data': data
            }
        except Exception as e:
            configs['extra_cfg.yml'] = {
                'path': str(extra_cfg_path),
                'data': {}
            }
    
    # Load plugin_vs_replay_cfg.yml
    plugin_cfg_path = cfg_path / "plugin_vs_replay_cfg.yml"
    if plugin_cfg_path.exists():
        try:
            with open(str(plugin_cfg_path), 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            configs['plugin_vs_replay_cfg.yml'] = {
                'path': str(plugin_cfg_path),
                'data': data
            }
        except Exception as e:
            configs['plugin_vs_replay_cfg.yml'] = {
                'path': str(plugin_cfg_path),
                'data': {}
            }
    
    return configs


def save_ini_targeted(file_path: str, section_updates: Dict[str, Dict[str, str]]) -> None:
    """
    Update specific keys in an INI file, preserving formatting and comments.
    
    Args:
        file_path: Path to INI file
        section_updates: Dict of section -> {key: value} pairs to update
    """
    path = Path(file_path)
    
    if not path.exists():
        return
    
    # Read original file
    with open(str(path), 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    # Parse INI for reference
    parser = configparser.ConfigParser()
    parser.read(str(path))
    
    # Build updated content
    new_lines = []
    current_section = None
    
    for line in original_lines:
        stripped = line.strip()
        
        # Check if this is a section header
        if stripped.startswith('[') and stripped.endswith(']'):
            current_section = stripped[1:-1]
            new_lines.append(line)
        # Check if this is a key-value line
        elif '=' in line and current_section and not stripped.startswith(';') and not stripped.startswith('#'):
            key = line.split('=')[0].strip()
            
            # Check if this key should be updated
            if current_section in section_updates and key in section_updates[current_section]:
                new_value = section_updates[current_section][key]
                new_lines.append(f"{key}={new_value}\n")
                del section_updates[current_section][key]
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add any remaining new sections/keys
    for section, updates in section_updates.items():
        if updates:
            new_lines.append(f"\n[{section}]\n")
            for key, value in updates.items():
                new_lines.append(f"{key}={value}\n")
    
    # Write updated file
    with open(str(path), 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


def save_yaml_targeted(file_path: str, scalar_updates: Dict[str, Any], 
                       enable_plugins: Optional[List[str]] = None) -> None:
    """
    Update specific keys in a YAML file, preserving comments where possible.
    
    Args:
        file_path: Path to YAML file
        scalar_updates: Dict of key: value pairs to update
        enable_plugins: List of plugins to enable (special handling)
    """
    if not yaml:
        return
    
    path = Path(file_path)
    
    if not path.exists():
        return
    
    # Read the file
    with open(str(path), 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse existing YAML
    with open(str(path), 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    
    # Apply scalar updates
    for key, value in scalar_updates.items():
        if value is not None:
            data[key] = value
    
    # Handle EnablePlugins
    if enable_plugins is not None:
        data['EnablePlugins'] = enable_plugins if enable_plugins else []
    
    # Write back as YAML (this is the safest approach)
    with open(str(path), 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def write_entry_list_ini(file_path: str, entry_list_data: List[Dict[str, str]]) -> None:
    """
    Write entry_list.ini file from entry data.
    
    Args:
        file_path: Path to entry_list.ini
        entry_list_data: List of entry dictionaries
    """
    path = Path(file_path)
    
    lines = []
    
    for idx, entry in enumerate(entry_list_data):
        section = f"CAR_{idx}"
        lines.append(f"\n[{section}]\n")
        lines.append(f"MODEL={entry.get('model', '')}\n")
        lines.append(f"SKIN={entry.get('skin', '')}\n")
        lines.append(f"SPECTATOR_MODE={entry.get('spectator_mode', '0')}\n")
        lines.append(f"DRIVERNAME={entry.get('drivername', '')}\n")
        lines.append(f"TEAM={entry.get('team', '')}\n")
        lines.append(f"GUID={entry.get('guid', '')}\n")
        lines.append(f"BALLAST={entry.get('ballast', '0')}\n")
        lines.append(f"RESTRICTOR={entry.get('restrictor', '0')}\n")
    
    # Write file
    with open(str(path), 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line)


# NOTE: update_data_track_params() removed - data_track_params.ini should NOT be modified
# as it contains reference configurations for all tracks in the AC content root
