## A Simple MTCNN Face Detection App

1. Install streamlit: `python3 -m pip install streamlit`

2. Run the app: `streamlit run main.py`


Minio

```
docker run -p 9000:9000 -e MINIO_ACCESS_KEY=minioadmin -e MINIO_SECRET_KEY=minioadmin -v /mnt/data:/data minio/minio server /data
```

PostgreSQL

```
docker run --name ossmi -e POSTGRES_PASSWORD=postgres -d -p 15432:5432 -v pgdata:/var/lib/postgresql/data postgres
```