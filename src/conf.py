import os
from PIL import Image
from typing import NamedTuple

DEFAULT_IMG = os.environ.get('DEFAULT_IMG', '/home/zhanibek/Desktop/projects/mtcnn_streamlit/data/imgs/DEFAULT.jpg')
DEFAULT_FONT = os.environ.get('DEFAULT_FONT', '/home/zhanibek/Desktop/projects/mtcnn_streamlit/data/fonts/Montserrat-Light.otf')
# Todo: Get font file via requests

main_img = Image.open(DEFAULT_IMG)


class Configs(NamedTuple):
    txt_font: str = DEFAULT_FONT
    txt_size: int = 30
    txt_color: str = 'white'
    rct_width: int = 1
