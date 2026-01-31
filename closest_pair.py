from database import get_embedding, get_image_key, get_database_size, get_nearest_neighbors_cosine
from pathlib import Path

def file_link(p: str) -> str:
    return Path(p).absolute().as_uri()

size = get_database_size()
smallest = []

for i in range(1, size):
    closest = get_nearest_neighbors_cosine(get_embedding(i))
    distance = closest[1][1]
    path = closest[1][0]

    if smallest == []:
        smallest = [path, get_image_key(i), distance]

    if smallest[2] > distance > 0.18:  # Distances below 0.18 tend to be the same person
        smallest = [path, get_image_key(i), distance]
        print(i, end=" ")
        print(file_link(smallest[0]), file_link(smallest[1]), distance)

print(smallest)