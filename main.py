from populate_database import populate_database, make_embedding
from database import get_nearest_neighbors_cosine, get_nearest_neighbors_l2
from PIL import Image

populate_database()

nearest = get_nearest_neighbors_cosine(make_embedding("download.jpeg"))
print(nearest)

def open_image(path: str) -> Image.Image:
    return Image.open(path)

for image in nearest:
    img = open_image(image[0])
    img.show()

