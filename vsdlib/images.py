import io
from typing import Dict, Optional, Tuple, Callable, List

from PIL.ImageDraw import Draw
from PIL.Image import Image, new as new_image
from PIL.ImageFont import truetype, FreeTypeFont

from .button_style import ButtonStyle


def img_to_bytes(img:Image):
    buf = io.BytesIO()
    img.rotate(180).save(buf, format='JPEG', quality=100, subsampling=0)
    return buf.getvalue()


# @functools.lru_cache
def generate_text_image(
    # size:Tuple[int,int]=(97,97),
    background_color:str,
    style:'ButtonStyle',
    text:str='',
    # background_color=light_purple,
    # text_color=black,
    # font_size=40,
):
    width, height = style.size
    img: Image = new_image("RGB", style.size, color=background_color)
    draw = Draw(img)

    textwidth: float = 0
    textheight: float = 0
    font: Optional[FreeTypeFont] = None
    text_fits = False
    font_size = style.font_size
    while not text_fits:
        font = truetype('SourceCodePro-Regular.otf', size=font_size)
        _, _, textwidth, textheight = draw.textbbox((0, 0), text, font)
        text_fits = textwidth <= width and textheight <= height
        font_size -= 1

    x = (width - textwidth) / 2
    y = (height - textheight) / 2
    draw.text((x, y), text, font=font, fill=style.text_color)
    return img_to_bytes(img)
