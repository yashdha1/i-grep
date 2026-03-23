from src.lib.db import init_db
from src.lib.get_paths import get_paths
from src.service.save_image import save
from src.lib.Timer import timer

@timer
def sync_data() : 
    init_db()  # Ensure database and tables exist
    paths = get_paths()
    print(paths)
    if not paths:
        print("No image path configured. Add a path to paths.txt (one per line).")
        return
    print("Saving images... might take few seconds.")
    for path in paths:
        save(path)
    print("Images saved successfully.\n")