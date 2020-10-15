import sys
sys.path.append('/home/zhanibek/Desktop/projects/ossmi')
import asyncio
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from src.conf import Configs, main_img
from src.services import Extractor, Faiss, PGClient, MinioClient


@st.cache
def get_face_extractor(threshold: float = 0.9):
    return Extractor(threshold=threshold)


def find_faces(image, configs=Configs()):
    with st.spinner('Detecting faces...'):
        draw = ImageDraw.Draw(im=image)
        font = ImageFont.truetype(font=configs.txt_font, size=configs.txt_size)

        embs = []
        for (emb, box, prob) in extractor.extract_face_embeddings(img=main_img):
            draw.rectangle(box.tolist(), width=configs.rct_width)
            draw.text(xy=(box[0], box[3]), text=f'{int(prob*100)} %', font=font, fill=configs.txt_color)
            show.image(image, caption='Uploaded Image', width=configs.q_img_width, use_column_width=False)
            # Todo: Save Face(bbox, prob, col_id, orig_img_id) into Minio, Postgres, Faiss.
            #  Consider caching and avoid duplicates
            embs.append(emb)
            # face = image.crop(box=box).resize(size=(160, 160), resample=2)
            # st.image(face)
        if not embs:
            st.warning('No Faces Detected!')
            return

        st.subheader("Similar Faces:")
        with Faiss(index_file=index_file) as fs:
            for dists, ids in fs.query_faces(embs=embs, k=5):
                # Get images with faces similar to a the detected faces
                faces = asyncio.run(pg_client.get_faces(ids=ids))
                for (face_id, face) in faces:
                    dist = dists[ids.tolist().index(face_id)]
                    # Get original images from Minio
                    sim_img = minio_client.get_image(bucket_name=bucket, object_name=face.orig_img)
                    draw = ImageDraw.Draw(im=sim_img)
                    draw.rectangle(face.bbox, width=configs.rct_width)
                    draw.text(xy=(face.bbox[0], face.bbox[3]), text=f'{int(face.prob * 100)} %', font=font, fill=configs.txt_color)
                    caption = f'Sim: {dist}. Face ID: {face_id}. Image from collection #{face.col_id}. Image: {face.orig_img}'
                    st.image(sim_img, caption=caption, width=configs.s_img_width, use_column_width=False)
                st.write('-' * 60)
        st.success('Done!')


st.title('Ossmi')
st.header('An Interactive Face Search App')
st.write("\n")

st.sidebar.title("Upload Photo")
st.set_option('deprecation.showfileUploaderEncoding', False)
uploaded_file = st.sidebar.file_uploader("", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    main_img = Image.open(uploaded_file)
    show = st.image(main_img, caption='Uploaded Image', width=500, use_column_width=False)
else:
    st.sidebar.write("Choose Your Own Image to Classify")
    show = st.image(main_img, caption='Default Image', width=500, use_column_width=False)


index_file = '/home/zhanibek/Desktop/projects/ossmi/demo/faces-personal.index'
bucket = 'personal'

pg_client = PGClient()
minio_client = MinioClient()
extractor = get_face_extractor(threshold=0.95)


if st.sidebar.button("Find Similar Faces"):
    find_faces(image=main_img)
