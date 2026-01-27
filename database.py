import os
import pg8000
from dotenv import load_dotenv
load_dotenv()

conn = pg8000.connect(
    user="faceapp",
    password=os.getenv("DB_PASSWORD"),
    host="localhost",
    port=5432,
    database="faceapp",
)

def add_embedding(image_key, embedding):
    vec = "[" + ",".join(map(str, embedding)) + "]"
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO faces (image_key, embedding) VALUES (%s, %s::vector)",
        (image_key, vec),
    )
    conn.commit()


def get_nearest_neighbors(embedding, top_k=5):
    vec = "[" + ",".join(map(str, embedding)) + "]"
    sql = """
        SELECT image_key, (embedding <=> %s::vector) AS dist
        FROM faces
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    cur = conn.cursor()
    cur.execute(sql, (vec, vec, top_k))
    return cur.fetchall()