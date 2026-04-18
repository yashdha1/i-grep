from pathlib import Path

import platformdirs

_APP = "igrep"


def data_dir() -> Path:
    """User data directory: DB and paths.txt.

    Windows : %APPDATA%\\igrep
    Linux   : ~/.local/share/igrep
    macOS   : ~/Library/Application Support/igrep
    """
    d = Path(platformdirs.user_data_dir(_APP))
    d.mkdir(parents=True, exist_ok=True)
    return d


def cache_dir() -> Path:
    """User cache directory: ML model files.

    Windows : %LOCALAPPDATA%\\igrep\\Cache
    Linux   : ~/.cache/igrep
    macOS   : ~/Library/Caches/igrep
    """
    d = Path(platformdirs.user_cache_dir(_APP))
    d.mkdir(parents=True, exist_ok=True)
    return d
