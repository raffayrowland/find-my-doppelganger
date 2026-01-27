from database import get_database_size, add_embedding
from deepface import DeepFace
import time
import os

def make_embedding(path):
    embedding = DeepFace.represent(
        img_path=path,
        model_name="Facenet512",
        detector_backend="skip",
        align=True,
        enforce_detection=True
    )[0]['embedding']
    return embedding

def populate_database():
    databaseSize = get_database_size()
    print(f"Database size: {databaseSize}")

    imgs = os.listdir("dataset")
    startTime = time.time()
    processed = 0
    for i in range(databaseSize, 70000):
        embedding = make_embedding(os.path.join("dataset", imgs[i]))
        add_embedding(image_key=os.path.join("dataset", imgs[i]),
                      embedding=embedding)
        processed += 1
        rate = processed / (time.time() - startTime)
        print(f"Processing image {i} at rate {rate:.2f}/s.  ETA: {(((70000 - i) / rate) // 60)} minutes")

