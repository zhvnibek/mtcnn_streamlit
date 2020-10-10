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

    def add_faces(self, embs: list, ids: list):
        """
        :param embs:
        :param ids:
        :return:
        """
        embs = np.array(embs)
        ids = np.array(ids)
        self.index.add_with_ids(embs, ids)
        print(f'{self.index.ntotal} items in index')

    def query_faces(self, embs: list, k: int = 5, threshold: float = 2.0):
        """Get images with faces similar to a the detected faces
        :param embs:
        :param k:
        :param threshold:
        :return:
        """
        embs = np.array(embs)
        dists_mt, ids_mt = self.index.search(embs, k)
        for dists, ids in zip(dists_mt, ids_mt):
            # Todo: # filter by distance threshold
            # for dist, id_ in zip(dists, ids):
            #     if dist < threshold:
            #         ...
            yield dists, ids


if __name__ == '__main__':
    with Faiss(index_file='../../src/faces.index') as fs:
        assert fs.index.is_trained
        print(fs.index.ntotal)
