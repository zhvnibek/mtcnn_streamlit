import os
import asyncio
from PIL import Image
from src.services import Extractor, Faiss, PGClient, Face

COL_ID = 1
index_file = '/home/zhanibek/Desktop/projects/ossmi/src/faces.index'
pg_client = PGClient()
extractor = Extractor()


def index_event(folder: str):
    print(folder)
    for file in os.listdir(folder):
        object_name = folder.split('/')[-1] + '/' + file
        img = Image.open(fp=os.path.join(folder, file))
        faces = []
        embs = []
        for (emb, box, prob) in extractor.extract_face_embeddings(img=img):
            faces.append(Face(col_id=COL_ID, orig_img=object_name, bbox=box, prob=prob))
            embs.append(emb)
        face_ids = asyncio.run(pg_client.insert_faces(faces=faces))
        if face_ids and embs and len(face_ids) == len(embs):
            with Faiss(index_file=index_file) as fs:
                fs.add_faces(embs=embs, ids=face_ids)

if __name__ == '__main__':
    events = '../data/imgs/events/'
    for event_dir in os.listdir(events):
        if event_dir.split('/')[-1] in ('37100',):
            continue
        event_dir = os.path.join(events, event_dir)
        index_event(folder=event_dir)
