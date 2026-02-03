from database import get_database_size, add_embedding
from deepface import DeepFace
import time
import os
from dotenv import load_dotenv
load_dotenv()

DATASET_PATH = os.getenv("DATASET_PATH")

def make_embedding(path):
    embedding = DeepFace.represent(
        img_path=path,
        model_name="Facenet512",
        detector_backend="skip",
        align=False,
        enforce_detection=True
    )[0]['embedding']
    return embedding

def make_embedding_aligned(path):
    embedding = DeepFace.represent(
        img_path=path,
        model_name="Facenet512",
        detector_backend="opencv",
        align=True,
        enforce_detection=True
    )[0]['embedding']
    return embedding

def generate_attributes(path):
    attributes = DeepFace.analyze(
        img_path=path,
        actions=['age', 'gender', 'race'],
        enforce_detection=False,
        silent=True
    )
    return attributes


# --- Only for use if populating database using images ---

def get_image_list():
    """
    This code was written for the ffhq dataset. If you want to use your own
    images, you will need to rewrite this function.
    :return: list of image paths
    """
    subfolders = os.listdir(DATASET_PATH)  # To use this, add the path to your .env file
    subfolders.remove('LICENSE.txt')
    all_files = []

    for folder in subfolders:
        images = os.listdir(os.path.join(DATASET_PATH, folder))
        for image in images:
            all_files.append(os.path.join(DATASET_PATH, folder, image))

    return all_files

def populate_database():
    databaseSize = get_database_size()
    print(f"Database size: {databaseSize}")

    imgs = get_image_list()
    startTime = time.time()
    processed = 0
    for i in range(databaseSize, 70000):
        attributes = generate_attributes(imgs[i])
        sex = 'F' if attributes[0]['dominant_gender'] == 'Woman' else 'M'
        age = attributes[0]['age']
        race = attributes[0]['dominant_race']
        embedding = make_embedding(imgs[i])
        add_embedding(image_key=imgs[i],
                      embedding=embedding,
                      age=age,
                      race=race,
                      sex=sex)
        processed += 1
        rate = processed / (time.time() - startTime)
        print(f"Processing image {i} at rate {rate:.2f}/s.  ETA: {(((70000 - i) / rate) // 60)} minutes")
