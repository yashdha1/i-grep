from src.lib.dirs import data_dir


def get_paths() -> list[str]:
    """Read paths from paths.txt (user data dir), one per line. Returns list of non-empty stripped lines."""
    paths_file = data_dir() / "paths.txt"
    if not paths_file.exists():
        return []
    return [line.strip() for line in paths_file.read_text().splitlines() if line.strip()]
