import os 

def formating(score: float, row, images_dir: str | None = None) -> str:
    loc = getattr(row, "image_loc", str(row))
    out = f"[{score:.3f}] {loc}"
    if images_dir:
        full = os.path.abspath(os.path.join(images_dir, loc))
        uri = "file:///" + full.replace("\\", "/")
        out += f"  {uri}"
    return out

def print_search_results(filtered, res=None, images_dir: str | None = None):
    """Print search results to console. results_with_scores: list of (score, row) for semantic, else None."""
    if res is not None:
        print(f"Found {len(res)} image(s).")
        for i, (score, row) in enumerate(res, 1):
            print(f"  {i}. {formating(score, row, images_dir=images_dir)}")
    else:
        print(f"\nFound {len(filtered)} image(s) with {len(filtered)} references.")
        for i, row in enumerate(filtered, 1):
            line = row.__str__()
            if images_dir and getattr(row, "image_loc", None):
                full = os.path.abspath(os.path.join(images_dir, row.image_loc))
                uri = "file:///" + full.replace("\\", "/")
                line += f"  {uri}"
            print(f"{i} : {line}")
