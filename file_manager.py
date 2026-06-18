"""
File management and discovery for the Assetto Corsa Server Configuration Manager
"""

from pathlib import Path
import shutil
from typing import Dict, List, Tuple


def discover_tracks(content_root: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Discover available tracks in content root.
    
    Returns:
        (track_list, track_display_map) where track_display_map maps display names to original names
    """
    if not content_root:
        return [], {}
    
    tracks_path = Path(content_root) / "tracks"
    if not tracks_path.exists():
        return [], {}
    
    track_list = []
    track_display_map = {}
    
    for track_dir in sorted(tracks_path.iterdir()):
        if track_dir.is_dir():
            track_name = track_dir.name
            display_name = track_name.replace('_', ' ').upper()
            track_list.append(display_name)
            track_display_map[display_name] = track_name
    
    return track_list, track_display_map


def discover_cars(content_root: str) -> Dict[str, str]:
    """
    Discover available cars in content root.
    
    Returns:
        Dictionary mapping original car names to formatted display names
    """
    if not content_root:
        return {}
    
    cars_path = Path(content_root) / "cars"
    if not cars_path.exists():
        return {}
    
    cars = {}
    
    for car_dir in sorted(cars_path.iterdir()):
        if car_dir.is_dir():
            car_name = car_dir.name
            display_name = car_name.replace('_', ' ').upper()
            cars[car_name] = display_name
    
    return cars


def discover_weather(content_root: str) -> List[str]:
    """
    Discover available weather presets in content root.
    
    Returns:
        List of weather names
    """
    if not content_root:
        return []
    
    weather_path = Path(content_root) / "weather"
    if not weather_path.exists():
        return []
    
    weather = []
    
    for weather_dir in sorted(weather_path.iterdir()):
        if weather_dir.is_dir():
            weather.append(weather_dir.name)
    
    return weather


def get_car_skins(content_root: str, car_name: str) -> List[str]:
    """
    Get available skins for a specific car.
    
    Args:
        content_root: Path to AC content root
        car_name: Name of the car
    
    Returns:
        List of skin names
    """
    if not content_root or not car_name:
        return []
    
    skins_path = Path(content_root) / "cars" / car_name / "skins"
    if not skins_path.exists():
        return []
    
    skins = []
    
    for skin_dir in sorted(skins_path.iterdir()):
        if skin_dir.is_dir():
            skins.append(skin_dir.name)
    
    return skins


def list_server_directories(servers_parent_dir: str) -> List[Tuple[str, str]]:
    """
    List all server directories.
    
    Args:
        servers_parent_dir: Parent directory containing servers
    
    Returns:
        List of (server_name, server_path) tuples
    """
    if not servers_parent_dir:
        return []
    
    parent_path = Path(servers_parent_dir)
    if not parent_path.exists():
        return []
    
    servers = []
    
    for item in sorted(parent_path.iterdir()):
        if item.is_dir():
            servers.append((item.name, str(item)))
    
    return servers


def copy_server_template(servers_parent_dir: str) -> str:
    """
    Copy the VS Server template to create a new server.
    Creates a new server folder and copies the contents of VS Server into it.
    
    Args:
        servers_parent_dir: Parent directory for servers
    
    Returns:
        Path to the new server folder
    """
    template_path = Path(__file__).parent / "VS Server"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found at {template_path}")
    
    parent_path = Path(servers_parent_dir)
    
    # Find unique name for the new server folder
    new_server_name = get_unique_folder_name(parent_path, "New Server")
    new_server_path = parent_path / new_server_name
    
    # Create the new server folder
    new_server_path.mkdir(parents=True, exist_ok=True)
    
    # Copy contents of VS Server template into the new server folder
    for item in template_path.iterdir():
        if item.is_dir():
            shutil.copytree(str(item), str(new_server_path / item.name))
        else:
            shutil.copy2(str(item), str(new_server_path / item.name))
    
    return str(new_server_path)


def duplicate_server(src_path: str, servers_parent_dir: str) -> str:
    """
    Duplicate an existing server.
    
    Args:
        src_path: Path to server to duplicate
        servers_parent_dir: Parent directory for servers
    
    Returns:
        Path to the new server
    """
    src_path = Path(src_path)
    parent_path = Path(servers_parent_dir)
    
    # Find unique name
    base_name = src_path.name + " (Copy)"
    new_name = get_unique_folder_name(parent_path, base_name)
    new_path = parent_path / new_name
    
    # Copy server
    shutil.copytree(str(src_path), str(new_path))
    
    return str(new_path)


def rename_server_folder(old_path: str, new_name: str) -> str:
    """
    Rename a server folder.
    
    Args:
        old_path: Current server path
        new_name: New server name
    
    Returns:
        Path to renamed server
    """
    old_path = Path(old_path)
    new_path = old_path.parent / new_name
    
    old_path.rename(new_path)
    
    return str(new_path)


def delete_server_folders(folder_paths: List[str]) -> List[str]:
    """
    Delete server folders.
    
    Args:
        folder_paths: List of server paths to delete
    
    Returns:
        List of error messages (empty if all succeeded)
    """
    errors = []
    
    for path in folder_paths:
        try:
            path = Path(path)
            if path.exists():
                shutil.rmtree(str(path))
        except Exception as e:
            errors.append(f"Failed to delete {path}: {str(e)}")
    
    return errors


def read_text_file(file_path: str) -> List[str]:
    """
    Read lines from a text file, excluding empty lines.
    
    Args:
        file_path: Path to file
    
    Returns:
        List of non-empty lines
    """
    path = Path(file_path)
    
    if not path.exists():
        return []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines
    except Exception:
        return []


def write_text_file(file_path: str, lines: List[str]) -> None:
    """
    Write lines to a text file.
    
    Args:
        file_path: Path to file
        lines: List of lines to write
    """
    path = Path(file_path)
    
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')


def get_unique_folder_name(parent_path: Path, base_name: str) -> str:
    """
    Generate a unique folder name.
    If base_name already exists, returns base_name (2), (3), etc.
    
    Args:
        parent_path: Parent directory path
        base_name: Desired folder name
    
    Returns:
        Unique folder name
    """
    parent_path = Path(parent_path)
    
    # Check if base name is available
    if not (parent_path / base_name).exists():
        return base_name
    
    # Find next available number
    counter = 2
    while (parent_path / f"{base_name} ({counter})").exists():
        counter += 1
    
    return f"{base_name} ({counter})"
