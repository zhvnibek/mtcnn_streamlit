import os
import asyncio
from PIL import Image
from src.model.extractor import Extractor
from src.db import Saver, Face
from src.model.indexer import Faiss

local_dsn = 'postgresql://postgres:postgres@localhost:15432/ossmi'
saver = Saver(dsn=local_dsn)

ext = Extractor()

COL_ID = 1


def index_event(folder: str):
    for file in os.listdir(folder):
        object_name = folder.split('/')[-1] + '/' + file
        img = Image.open(fp=os.path.join(folder, file))
        faces = []
        embs = []
        for (emb, box, prob) in ext.extract_faces_embeddings(img=img):
            faces.append(Face(col_id=COL_ID, orig_img=object_name, bbox=box, prob=prob))
            embs.append(emb)
        face_ids = asyncio.run(saver.insert_faces(faces=faces))

        if face_ids and embs and len(face_ids) == len(embs):
            with Faiss(index_file='model/faces.index') as fs:
                fs.insert_embeddings(embs=embs, ids=face_ids)

if __name__ == '__main__':

    events = '../data/imgs/events/'
    for event_dir in os.listdir(events):
        if event_dir in ('36948', '36992'):
            continue
        event_dir = os.path.join(events, event_dir)
        index_event(folder=event_dir)
