import io
import os
from typing import Dict, Optional, Tuple, Callable, List

from PIL.ImageDraw import Draw
from PIL.Image import Image, new as new_image
from PIL.ImageFont import truetype, FreeTypeFont
from PIL import Image as PILImage

from .button_style import ButtonStyle
from .colors import light_purple


emoji_font_filepath = os.path.join('Noto_Color_Emoji', 'NotoColorEmoji-Regular.ttf')


def img_to_bytes(img:Image, rotate:bool=False) -> bytes:
    buf = io.BytesIO()
    if rotate:
        img = img.rotate(180)
    # else:
    #     img = img.rotate(90+180)
    img.save(buf, format='JPEG', quality=100, subsampling=0)
    return buf.getvalue()


def rotate_image(image: Image, degrees: int) -> Image:
    return image.rotate(-degrees)  # Negative degree for clockwise rotation

# @functools.lru_cache
def generate_text_image(
    # size:Tuple[int,int]=(97,97),
    background_color:str,
    style:'ButtonStyle',
    text:str='',
    rotate:bool=False,
    # background_color=light_purple,
    # text_color=black,
    # font_size=40,
):
    width, height = style.__class__.size
    img: Image = new_image("RGB", style.size, color=background_color)
    draw = Draw(img)

    textwidth: float = 0
    textheight: float = 0
    font: Optional[FreeTypeFont] = None
    text_fits = False
    font_size = int(style.font_size)
    while not text_fits:
        font = truetype('SourceCodePro-Regular.otf', size=font_size)
        # font = truetype(emoji_font_filepath, size=font_size)
        # font = truetype('NotoColorEmoji.ttf', size=109)
        try:
            _, _, textwidth, textheight = draw.textbbox((0, 0), text, font)
        except Exception as e:
            print(e, text, font)
            raise
        text_fits = textwidth <= width and textheight <= height
        font_size -= 1

    x = (width - textwidth) / 2
    y = (height - textheight) / 2
    draw.text((x, y), text, font=font, fill=style.text_color)
    # if rotate:
    # img = rotate_image(img, 90)
    img = rotate_image(img, 180)
    return img_to_bytes(img)


def generate_emoji_image(
    background_color:str=light_purple,
    style:'ButtonStyle'=ButtonStyle(),
    text:str='',
):
    width, height = style.__class__.size
    img: Image = new_image("RGB", style.size, color=background_color)
    draw = Draw(img)

    textwidth: float = 0
    textheight: float = 0
    font: Optional[FreeTypeFont] = None
    font = truetype('SourceCodePro-Regular.otf', size=109)

    x = (width - textwidth) / 2
    y = (height - textheight) / 2
    draw.text((x, y), text, font=font, fill=style.text_color)
    return img_to_bytes(img)


def load_button_image(filepath:str, size:Tuple[int,int], rotate:int=0) -> bytes:
    image = PILImage.open(filepath)
    N, M = size # Sample values
    image_resized = image.resize((N, M))
    buffer = io.BytesIO()
    image_resized.save(buffer, format="JPEG")
    image_jpeg = PILImage.open(buffer)
    image_rotated = image_jpeg.rotate(rotate, expand=True)
    final_buffer = io.BytesIO()
    image_rotated.save(final_buffer, format="JPEG")
    image_bytes = final_buffer.getvalue()
    return image_bytes
