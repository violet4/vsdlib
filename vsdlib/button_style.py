from typing import Tuple, Optional,Union

from .colors import light_purple, dark_purple, black


class ButtonStyle:
    size: Tuple[int,int]
    background_color: str = light_purple
    pressed_background_color: str = dark_purple
    text_color: str = black
    font_size: Union[int,str] = 40
    image_path: Optional[str]

    def __init__(
        self,
        background_color=light_purple,
        text_color=text_color,
        font_size:Union[int,str]=font_size,
        pressed_background_color=pressed_background_color,
        image_path=None,
    ):
        self.background_color = background_color
        self.text_color = text_color
        self.font_size = font_size
        self.pressed_background_color = pressed_background_color
        self.image_path = image_path

    @classmethod
    def set_size(cls, size:Tuple[int,int]):
        cls.size = size

