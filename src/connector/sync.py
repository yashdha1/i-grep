from src.lib.db import init_db
from src.service.save_image import save_images
import os 
from src.lib.Timer import timer

@timer
def sync_data() : 
    init_db()  # Ensure database and tables exist
    print("Saving images... might take few seconds.")
    save_images(os.getenv("IMAGE_DIR"))
    print("Images saved successfully.\n")