-- enable pgvector in this DB
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS faces (
    id bigserial PRIMARY KEY,
    image_key text NOT NULL,        -- path
    age int NOT NULL,
    sex char(1) NOT NULL CHECK (sex IN ('F', 'M')),
    race VARCHAR(20) NOT NULL
        CHECK (race IN ('asian', 'white', 'middle eastern', 'indian', 'latino hispanic', 'black')),
    embedding vector(512) NOT NULL
);

-- for cosine distance search (recommended for normalized embeddings)
CREATE INDEX IF NOT EXISTS faces_embedding_hnsw_cosine
  ON faces USING hnsw (embedding vector_cosine_ops);

-- Optional l2 index:
-- CREATE INDEX IF NOT EXISTS faces_embedding_hnsw_l2
--   ON faces USING hnsw (embedding vector_l2_ops);

