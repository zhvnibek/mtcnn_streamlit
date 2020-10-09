import asyncio
import faiss
import numpy as np
import streamlit as st
from torchvision import transforms
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import fixed_image_standardization
from conf import Configs, FACES_INDEX, main_img
from model.extractor import Extractor
from model.indexer import Faiss
from db import Saver
from minio_ import MinioClient

pil2tensor = transforms.Compose([np.float32, transforms.ToTensor(), fixed_image_standardization])


@st.cache
def get_face_extractor():
    return Extractor()

kipyatcom = 'kipyatcom'
index_file = '/home/zhanibek/Desktop/projects/mtcnn_streamlit/src/model/faces.index'
local_dsn = 'postgresql://postgres:postgres@localhost:15432/ossmi'
saver = Saver(dsn=local_dsn)

mc = MinioClient()


@st.cache(hash_funcs={faiss.swigfaiss.IndexIVFFlat: lambda _: 1})
def get_index():
    return faiss.read_index(FACES_INDEX)


def detect_faces(image, configs=Configs()):
    with st.spinner('Detecting faces...'):
        draw = ImageDraw.Draw(im=image)
        font = ImageFont.truetype(font=configs.txt_font, size=configs.txt_size)
        embs = []
        for (emb, box, prob) in ext.extract_face_embeddings(img=main_img):
            draw.rectangle(box.tolist(), width=configs.rct_width)
            draw.text(xy=(box[0], box[3]), text=f'{int(prob*100)} %', font=font, fill=configs.txt_color)
            show.image(image, 'Uploaded Image', use_column_width=True)
            # Todo: Save Face(bbox, prob, col_id, orig_img_id) into Minio, Postgres, Faiss
            embs.append(emb)
            # face = image.crop(box=box).resize(size=(160, 160), resample=2)
            # st.image(face)
        embs = np.array(embs)

        st.subheader("Similar images:")
        with Faiss(index_file=index_file) as fs:
            dists_mt, ids_mt = fs.index.search(embs, 5)  # tune both count and distance threshold

            for dists, ids in zip(dists_mt, ids_mt):
                # Get images with faces similar to a the detected face
                faces = asyncio.run(saver.get_faces(ids=ids))
                for (face_id, face) in faces:
                    dist = dists[ids.tolist().index(face_id)]
                    # st.write(face_id, face.orig_img, dist)
                    sim_img = mc.get_image(bucket_name=kipyatcom, object_name=face.orig_img)
                    st.image(sim_img, caption=f'Sim: {dist}', use_column_width=True)
                st.write('=' * 30)

        st.success('Done!')


st.title('Simple MTCNN Face Detector')
st.write("\n")

st.sidebar.title("Upload Image")
st.set_option('deprecation.showfileUploaderEncoding', False)
uploaded_file = st.sidebar.file_uploader("", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    main_img = Image.open(uploaded_file)
    show = st.image(main_img, caption='Uploaded Image', use_column_width=True)
else:
    st.sidebar.write("Choose Your Own Image to Classify")
    show = st.image(main_img, caption='Default Image', use_column_width=True)

th: float = st.sidebar.slider(
    'Pick a probability threshold:',
    0.5, 1.0, 0.8
)

ext = get_face_extractor()
if st.sidebar.button("Detect Faces"):
    detect_faces(image=main_img)
