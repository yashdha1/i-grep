import os

from src.lib.get_paths import get_paths


def formating(score: float, row, images_dir: str | None = None) -> str:
    loc = getattr(row, "image_loc", str(row))
    out = f"[{score:.3f}] {loc}"
    if images_dir:
        full = os.path.abspath(os.path.join(images_dir, loc))
        uri = "file:///" + full.replace("\\", "/")
        out += f"  {uri}"
    return out


import re

GREEN = "\033[32m"
RESET = "\033[0m"


def _highlight(text: str, pattern: str, ignore_case: bool = False) -> str:
    flags = re.IGNORECASE if ignore_case else 0
    return re.sub(f"({re.escape(pattern)})", f"{GREEN}\\1{RESET}", text, flags=flags)


def print_search_results(filtered, res=None, limit: int = 5, pattern: str | None = None, ignore_case: bool = False):
    """Print search results to console. results_with_scores: list of (score, row) for semantic, else None."""
    paths = get_paths()
    images_dir = paths[0] if paths else None
    if res is not None:
        shown = res[:limit]
        print(f"Found {len(res)} image(s).")
        for i, (score, row) in enumerate(shown, 1):
            print(f"  {i}. {formating(score, row, images_dir=images_dir)}")
    else:
        shown = filtered[:limit]
        print(f"\nFound {len(filtered)} image(s) with {len(filtered)} references.")
        for i, row in enumerate(shown, 1):
            line = row.__str__()
            if images_dir and getattr(row, "image_loc", None):
                full = os.path.abspath(os.path.join(images_dir, row.image_loc))
                uri = "file:///" + full.replace("\\", "/")
                line += f"  {uri}"
            if pattern:
                line = _highlight(line, pattern, ignore_case=ignore_case)
            print(f"{i} : {line}")
