from pathlib import Path


def get_paths() -> list[str]:
    """Read paths from paths.txt (project root), one per line. Returns list of non-empty stripped lines."""
    paths_file = Path(__file__).resolve().parent.parent.parent / "paths.txt"
    if not paths_file.exists():
        return []
    return [line.strip() for line in paths_file.read_text().splitlines() if line.strip()]
