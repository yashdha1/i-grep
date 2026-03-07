from src.lib.db import init_db
from src.lib.llm import download_and_save_model_locally
from src.lib.Timer import timer

@timer
def setup():
    try:
        print("Setting up the application, INITIAL SEETUP MAY TAKE FEW SECONDS. ")
        # 1. setup the databases
        print("Initializing database...")
        init_db()
        print("Database initialized successfully.\n")

        # 2. setup the models (download the model and save it locally)
        download_and_save_model_locally()
        print("Model downloaded successfully.\n")
    except Exception as e:
        print(f"Error setting up the application: {e}")
        return False
    return True