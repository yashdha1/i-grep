from src.lib.db import init_db
from src.lib.llm import download_and_save_model_locally
from src.lib.Timer import timer

@timer
def setup():
    try:
        print("Setting up the application. Initial setup may take a few seconds.")
        print("Initializing database...")
        init_db()
        print("Database initialized successfully.\n")

        download_and_save_model_locally()
        print("Model ready.\n")
    except Exception as e:
        print(f"Error setting up the application: {e}")
        return False
    return True