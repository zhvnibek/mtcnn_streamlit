import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN
from conf import Configs, main_img


@st.cache
def get_model():
    st.write('Preparing MTCNN model...')
    return MTCNN(keep_all=True)


def detect_faces(model, image, threshold: float, configs=Configs()):
    with st.spinner('Detecting faces...'):
        draw = ImageDraw.Draw(im=image)
        font = ImageFont.truetype(font=configs.txt_font, size=configs.txt_size)
        boxes, probs = model.detect(img=image, landmarks=False)
        for box, prob in zip(boxes, probs):
            if prob > threshold:
                draw.rectangle(box.tolist(), width=configs.rct_width)
                draw.text(xy=(box[0], box[3]), text=f'{int(prob*100)} %', font=font, fill=configs.txt_color)
                show.image(image, 'Uploaded Image', use_column_width=True)
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

mtcnn = get_model()
if st.sidebar.button("Detect Faces"):
    detect_faces(model=mtcnn, image=main_img, threshold=th)
