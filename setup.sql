CREATE DATABASE faceapp OWNER faceapp;
\connect faceapp

-- enable pgvector in this DB
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS faces (
  id bigserial PRIMARY KEY,
  image_key text NOT NULL,        -- path / S3 key / URL pointer
  embedding vector(512) NOT NULL, -- change 512 if your model differs
  created_at timestamptz DEFAULT now()
);

-- for cosine distance search (recommended for normalized embeddings)
CREATE INDEX IF NOT EXISTS faces_embedding_hnsw_cosine
  ON faces USING hnsw (embedding vector_cosine_ops);

-- Optional l2 index:
-- CREATE INDEX IF NOT EXISTS faces_embedding_hnsw_l2
--   ON faces USING hnsw (embedding vector_l2_ops);

