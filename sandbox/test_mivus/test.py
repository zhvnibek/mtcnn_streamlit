import time
import random
from milvus import Milvus, IndexType, MetricType, Status

milvus = Milvus(host='localhost', port='19530')

dim = 512
col_name = 'faces'
param = {'collection_name': col_name, 'dimension': dim, 'index_file_size': 1024, 'metric_type': MetricType.L2}
milvus.create_collection(param=param)

ivf_param = {'nlist': 16384}
milvus.create_index(collection_name=col_name, index_type=IndexType.IVF_FLAT, params=ivf_param)

vectors = [[random.random() for _ in range(dim)] for _ in range(2000)]
vector_ids = list(range(2000))
_, ids = milvus.insert(collection_name=col_name, records=vectors, ids=vector_ids)
# print(ids)

time.sleep(1)
search_param = {'nprobe': 16}
q_records = [[random.random() for _ in range(dim)] for _ in range(5)]
_, result = milvus.search(collection_name=col_name, query_records=q_records, top_k=2, params=search_param)
# for r in result:
#     print(r)
print(result.id_array)
print(result)

milvus.drop_collection(collection_name=col_name)

milvus.close()
