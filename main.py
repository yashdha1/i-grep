from src.lib.db import SessionLocal
from src.models.Image import Image
from src.service.save_image import save_images
from src.service.search_pattern import search_images_keyword
from src.service.filters import filter_rows
from src.service.console_output import print_search_results
from src.lib.llm import search_embeddings


def main(): 
    IMAGES_DIR = "./images"
    while True : 
        
        print("  0. Update the database and embeddings.")
        print("  1. Keyword search.")
        print("  2. Semantic search.")
        choice = input(">> ").strip()

        if choice == "0" : 
            print("Saving images... might take few seconds.")
            save_images(IMAGES_DIR)
            print("Images saved successfully.\n")
        
        elif choice == "1":
            query = input("Query: ").strip()
            if not query:
                print("No query provided.")
                return
            rows = search_images_keyword(query, 5)
            filtered = filter_rows(rows, query)
            print_search_results(filtered, images_dir=IMAGES_DIR)

        elif choice == "2":
            query = input("Query: ").strip()
            if not query:
                print("No query provided.")
                return
            with SessionLocal() as session:
                db_rows = session.query(Image).all()
            results = search_embeddings(query, db_rows, top_k=5)
            print_search_results(None, results, images_dir=IMAGES_DIR)

        else:
            print("Invalid choice. Use 1 or 2.")
            break


if __name__ == "__main__":
    main()
