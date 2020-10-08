import asyncpg
from typing import List, NamedTuple
from asyncpg.connection import Connection


class Face(NamedTuple):
    bbox: List[float]
    prob: float
    orig_img: str
    col_id: int


class Saver:

    def __init__(self, dsn: str):
        self.dsn = dsn

    async def insert_faces(self, faces: List[Face]) -> List[int]:
        conn: Connection = await asyncpg.connect(dsn=self.dsn)
        stmt = await conn.prepare(
            query='''INSERT INTO faces (bbox, prob, orig_img, col_id) VALUES ($1, $2, $3, $4) RETURNING id'''
        )
        _ids = []
        async with conn.transaction():
            for face in faces:
                _id = await stmt.fetchval(face.bbox, face.prob, face.orig_img, face.col_id)
                _ids.append(_id)
        return _ids
