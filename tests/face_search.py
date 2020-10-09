import asyncio
import numpy as np
from PIL import Image
from src.conf import main_img
from src.model.indexer import Faiss
from src.model.extractor import Extractor
from src.db import Saver

# visualize distances in neo4j
# many-to-many faces relation

main_img = Image.open('/home/zhanibek/Desktop/projects/mtcnn_streamlit/data/imgs/events/37093/KIPYATCOM_001.jpg')

ext = Extractor()
local_dsn = 'postgresql://postgres:postgres@localhost:15432/ossmi'
saver = Saver(dsn=local_dsn)

embs = []
for (emb, box, prob) in ext.extract_face_embeddings(img=main_img):
    # print(emb.shape, box, prob)
    # Todo: Save Face(bbox, prob, col_id, orig_img_id) into Minio, Postgres, Faiss
    embs.append(emb)

embs = np.array(embs)

with Faiss(index_file='../src/model/faces.index') as fs:
    dists_mt, ids_mt = fs.index.search(embs, 5)  # tune both count and distance threshold

    for dists, ids in zip(dists_mt, ids_mt):
        # Get images with faces similar to a the detected face
        faces = asyncio.run(saver.get_faces(ids=ids))
        for (face_id, face) in faces:
            dist = dists[ids.tolist().index(face_id)]
            print(face_id, face.orig_img, dist)
        print('='*30)
