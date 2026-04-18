from pathlib import Path

from src.lib.dirs import data_dir


def get_paths_file() -> Path:
    """Get the absolute path to paths.txt (user data dir)."""
    return data_dir() / "paths.txt"


def add_path(folder_path: str) -> None:
    """Add a folder path to paths.txt if not already present."""
    paths_file = get_paths_file()
    
    # Normalize the path (handle both absolute and relative)
    folder_path = Path(folder_path).resolve().as_posix()
    
    # Read existing paths
    existing_paths = set()
    if paths_file.exists():
        existing_paths = {
            line.strip() for line in paths_file.read_text().splitlines() 
            if line.strip()
        }
    
    # Add new path if not already present
    if folder_path not in existing_paths:
        with open(paths_file, "a") as f:
            if existing_paths:  # Add newline if file has content
                f.write("\n")
            f.write(folder_path + "\n")
        print(f"✓ Added path: {folder_path}")
    else:
        print(f"✓ Path already tracked: {folder_path}")


def list_paths() -> list[str]:
    """List all tracked folder paths."""
    paths_file = get_paths_file()
    if not paths_file.exists():
        return []
    return [
        line.strip() for line in paths_file.read_text().splitlines() 
        if line.strip()
    ]


def remove_path(folder_path: str) -> None:
    """Remove a folder path from paths.txt."""
    paths_file = get_paths_file()
    
    # Normalize the path
    folder_path = Path(folder_path).resolve().as_posix()
    
    if not paths_file.exists():
        print("No paths.txt found.")
        return
    
    # Read existing paths
    existing_paths = [
        line.strip() for line in paths_file.read_text().splitlines() 
        if line.strip()
    ]
    
    # Filter out the path to remove
    new_paths = [p for p in existing_paths if Path(p).resolve().as_posix() != folder_path]
    
    if len(new_paths) < len(existing_paths):
        # Write back the updated paths
        with open(paths_file, "w") as f:
            for path in new_paths:
                f.write(path + "\n")
        print(f"✓ Removed path: {folder_path}")
    else:
        print(f"✗ Path not found: {folder_path}")
