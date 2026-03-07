from src.lib.db import SessionLocal
from src.models.Image import Image
from src.service.extractor import extract_text_from_image
from src.lib.llm import encode_text
from src.lib.Timer import timer
import json
import os

 


@timer
def save_images(directory_path: str):
    """Save all images in the directory to the database."""
    try : 
        with SessionLocal() as db:
            for image_path in os.listdir(directory_path):
                full_path = os.path.join(directory_path, image_path)

                image_already_exists = db.query(Image).filter(Image.image_loc == image_path).first()
                if image_already_exists:
                    continue 
                text = extract_text_from_image(full_path)
                embedding_vec = encode_text(text)
                embeddings = json.dumps(embedding_vec.tolist())
                image = Image(image_loc=image_path, words=text or "", embeddings=embeddings)
                db.add(image) 
                
            print(f"Saved {len(os.listdir(directory_path))} images")
            db.commit()
            print("Images saved successfully")
    except Exception as e:
        print(f"Error saving images: {e}")
        return False
    return True