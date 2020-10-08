import faiss
import numpy as np
import streamlit as st
from torch import unsqueeze
from torchvision import transforms
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1, fixed_image_standardization
from conf import Configs, FACES_INDEX, main_img

pil2tensor = transforms.Compose([np.float32, transforms.ToTensor(), fixed_image_standardization])


@st.cache
def get_mtcnn():
    st.write('Preparing MTCNN model...')
    return MTCNN(keep_all=True)


@st.cache
def get_resnet():
    net = InceptionResnetV1(
        classify=False,
        pretrained='vggface2'
    ).to('cpu')
    _ = net.eval()
    return net


@st.cache(hash_funcs={faiss.swigfaiss.IndexIVFFlat: lambda _: 1})
def get_index():
    return faiss.read_index(FACES_INDEX)


def detect_faces(image, threshold: float, configs=Configs()):
    with st.spinner('Detecting faces...'):
        draw = ImageDraw.Draw(im=image)
        font = ImageFont.truetype(font=configs.txt_font, size=configs.txt_size)
        mtcnn = get_mtcnn()
        boxes, probs = mtcnn.detect(img=image, landmarks=False)
        for box, prob in zip(boxes, probs):
            if prob > threshold:
                draw.rectangle(box.tolist(), width=configs.rct_width)
                draw.text(xy=(box[0], box[3]), text=f'{int(prob*100)} %', font=font, fill=configs.txt_color)
                show.image(image, 'Uploaded Image', use_column_width=True)
                face = image.crop(box=box).resize(size=(mtcnn.image_size, mtcnn.image_size), resample=2)
                st.image(face)
                face = unsqueeze(pil2tensor(face), dim=0)
                face_emb = get_resnet()(face)
                face_emb = face_emb.detach().numpy()
                index = get_index()
                distances, indices = index.search(face_emb, 5)
                # query minio by ids (indices)
                st.write('='*20)

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

if st.sidebar.button("Detect Faces"):
    detect_faces(image=main_img, threshold=th)
