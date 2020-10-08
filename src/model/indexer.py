import faiss
import numpy as np


class Faiss:

    def __init__(self, index_file: str):
        # self.index = Faiss.create_index()
        self._index_file = index_file
        self.index = None

    def __enter__(self):
        self.index = faiss.read_index(self._index_file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        faiss.write_index(self.index, self._index_file)

    @staticmethod
    def create_index(dim: int = 512, cells: int = 100):
        return faiss.IndexIVFFlat(faiss.IndexFlatL2(dim), dim, cells)

    def insert_embeddings(self, embs: list, ids: list):
        embs = np.array(embs)
        ids = np.array(ids)
        self.index.add_with_ids(embs, ids)
        print(f'{self.index.ntotal} items in index')

if __name__ == '__main__':
    with Faiss(index_file='faces.index') as fs:
        assert fs.index.is_trained
        print(fs.index.ntotal)
