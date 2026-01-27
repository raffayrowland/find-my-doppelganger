from deepface import DeepFace
import os
from database import add_embedding, get_nearest_neighbors

def make_embedding(path):
    embedding = DeepFace.represent(
        img_path=path,
        model_name="ArcFace",
        detector_backend="retinaface",
        align=True,
        enforce_detection=True
    )[0]['embedding']
    return embedding

imgs = os.listdir("Humans")
print(imgs)
for i in range(100):
    print(f"Processing image {i}:  Humans/{imgs[i]}")
    embedding = make_embedding(os.path.join("Humans", imgs[i]))
    add_embedding(image_key=os.path.join("Humans", imgs[i]), embedding=embedding)

print(get_nearest_neighbors(make_embedding("front.jpeg")))
