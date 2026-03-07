from src.lib.db import init_db
from src.service.save_image import save_images
from src.service.search_pattern import search_images_keyword
from src.service.filters import filter_rows

def main() : 
    print("Hello from igrep!")
    init_db()
    print("Database initialized successfully")

    print("Saving images...")
    save_images("./images")
    print("Images saved successfully")

    query = input("Enter a query: ")
    if query == "":
        print("No query  provided.")
        return 


    rows = search_images_keyword(query, 5)
    print(f"Found {len(rows)} images." , end=" ")
    if len(rows) == 0: 
        print("No Match found.")
        return
    rows = filter_rows(rows, query)
    
    print(f"with {len(rows)} references.")
    
    for r in rows:
        print(r.__str__())

if __name__ == "__main__":
    main()
