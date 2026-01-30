from database import get_embedding, get_image_key, get_database_size, get_nearest_neighbors_cosine

size = get_database_size()
smallest = []

for i in range(1, size):
    closest = get_nearest_neighbors_cosine(get_embedding(i))
    distance = closest[1][1]
    path = closest[1][0]

    if smallest == []:
        smallest = [path, get_image_key(i), distance]

    if distance < smallest[2]:
        smallest = [path, get_image_key(i), distance]

    print(i, smallest)

print(smallest)