# Find my doppelgänger 

Utilises facial embeddings and a Postgres (pgvector) database / cosine similarity to find the face that most closely resembles the query face. Dataset contains 70k faces from ffhq (more info below), pre-embedded using Facenet512.

---

# Tech stack
- Python 3.12
- Deepface / Facenet512
- Postgres / pgvector
- Nvidia ffhq dataset

# Demo
All query images used for these demos were generated using [thispersondoesnotexist.com](https://thispersondoesnotexist.com/), and results are from the ffhq dataset. The query image is the large one on top, and the results are the 5 smaller images.

<img src="images/example2_with_results.png" width="600" alt="Demo 1">

<img src="images/example_with_results.png" width="600" alt="Demo 2">

<img src="images/example3_with_results.png" width="600" alt="Demo 3">

--- 

# Prerequisites

- PostgreSQL
- pgvector
- Python 3.12
- sql_dump.sql file downloaded

--- 

# Installation
### Clone the repository and set up the environment:
```
git clone https://github.com/raffayrowland/find-my-doppelganger.git 
cd find-my-doppelganger
pip install -r requirements.txt
touch .env
```
### Set up Postgres database:
```
createuser -P faceapp  -- Set password and remember it
createdb -O faceapp faceapp
```
### Run inside the faceapp database:
```
psql -d faceapp -f setup.sql
```
### Add this line to your .env file:
```
DB_PASSWORD="{insert your db password here}"
```

--- 

# Dataset
- Used Nvidia's ffhq dataset
- Specifically, the 1024x1024 portion
- [Dataset repo](https://github.com/NVlabs/ffhq-dataset)

--- 

## Citations

If you use this project in academic work, please cite:

- DeepFace (library used to generate/query embeddings; FaceNet512 via DeepFace):
  - Serengil, S. I., & Ozpinar, A. (2020). *LightFace: A Hybrid Deep Face Recognition Framework*. 2020 Innovations in Intelligent Systems and Applications Conference (ASYU). DOI: 10.1109/ASYU50717.2020.9259802
  - (Optional) Serengil, S. I., & Ozpinar, A. (2021). *HyperExtended LightFace: A Facial Attribute Analysis Framework*. 2021 International Conference on Engineering and Emerging Technologies (ICEET). DOI: 10.1109/ICEET53442.2021.9659697

- FaceNet (embedding model):
  - Schroff, F., Kalenichenko, D., & Philbin, J. (2015). *FaceNet: A Unified Embedding for Face Recognition and Clustering*. CVPR 2015. arXiv:1503.03832

- FFHQ dataset:
  - Karras, T., Laine, S., & Aila, T. (2019). *A Style-Based Generator Architecture for Generative Adversarial Networks*. CVPR 2019. arXiv:1812.04948
  - Also cite the FFHQ repository / metadata if appropriate.

- HNSW (ANN index used by pgvector):
  - Malkov, Y. A., & Yashunin, D. A. (2016). *Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs*. arXiv:1603.09320

- pgvector (vector similarity search in Postgres):
  - Kane, A. *pgvector: Open-source vector similarity search for Postgres*. GitHub repository: https://github.com/pgvector/pgvector
