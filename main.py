from src.lib.db import init_db
from src.service.save_image import save_images
from src.service.search_pattern import search_images_keyword

def main() : 
    print("Hello from igrep!")
    # init_db()
    # print("Database initialized successfully")

    # print("Saving images...")
    # save_images("./images")
    # print("Images saved successfully")


    rows = search_images_keyword("zen")
    print(f"Found {len(rows)} images.")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
