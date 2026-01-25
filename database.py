import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = "postgresql://faceapp:" + os.getenv("DB_PASSWORD") + "@localhost:5432/faceapp"

def add_embedding(image_key, embedding):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO faces (image_key, embedding) VALUES (%s, %s)", (image_key, embedding))

        conn.commit()


def get_nearest_neighbors(embedding, top_k=5):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT image_key, (embedding <=> %s) AS dist FROM faces ORDER BY embedding <=> %s LIMIT %s", (embedding, embedding, top_k))
            rows = cursor.fetchall()
            return rows