from deepface import DeepFace

# 1) Put your candidate faces in a folder, e.g.
#    db/
#      alice.jpg
#      bob.png
#      charlie.jpeg
#
# 2) Put the user upload as query.jpg

query_path = "unnamed.jpg"
db_path = "imgs"

# Returns a pandas DataFrame (wrapped in a list) of best matches sorted by distance
embedding: list[dict] = DeepFace.represent(img_path=query_path, model_name="ArcFace")

print(embedding)
