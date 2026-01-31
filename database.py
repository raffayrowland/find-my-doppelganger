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


def get_nearest_neighbors_cosine(embedding, top_k=5):
    if type(embedding) != str:
        vec = "[" + ",".join(map(str, embedding)) + "]"
    else:
        vec = embedding
    sql = """
        SELECT image_key, (embedding <=> %s::vector) AS dist
        FROM faces
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    cur = conn.cursor()
    cur.execute(sql, (vec, vec, top_k))
    return cur.fetchall()

def get_nearest_neighbors_l2(embedding, top_k=5):
    vec = "[" + ",".join(map(str, embedding)) + "]"
    sql = """
        SELECT image_key, (embedding <-> %s::vector) AS dist
        FROM faces
        ORDER BY embedding <-> %s::vector
        LIMIT %s
    """
    cur = conn.cursor()
    cur.execute(sql, (vec, vec, top_k))
    return cur.fetchall()

def get_embedding(id):
    cur = conn.cursor()
    cur.execute(
        "SELECT embedding FROM faces WHERE id = %s",
        (id,)
    )
    return cur.fetchone()[0]

def get_image_key(id):
    cur = conn.cursor()
    cur.execute(
        "SELECT image_key FROM faces WHERE id = %s",
        (id,)
    )
    return cur.fetchone()[0]

def get_database_size():
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM faces"
    )
    return cur.fetchone()[0]