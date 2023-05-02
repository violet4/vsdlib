import inspect
import functools
from typing import Optional, Callable, List


from StreamDeck.Devices.StreamDeck import StreamDeck

from .images import generate_text_image
from .button_style import ButtonStyle


class Button:
    sd: StreamDeck
    fn: Callable
    name: Optional[str]
    pressed: bool
    on_keydown_callbacks: List[Callable]
    on_keyup_callbacks: List[Callable]
    style: ButtonStyle
    text: str
    slot: Optional['ButtonSlot']

    def __init__(
        self,
        fn:Optional[Callable]=None, name:Optional[str]=None,
        text:Optional[str]='',
        button_switches_page:bool=False, style:ButtonStyle=ButtonStyle(),
    ):
        self.slot = None
        self.fn = self.ensure_param_count()(self.handle_button_event if fn is None else fn)
        self.name = name
        self.pressed = False
        self.on_keydown_callbacks = []
        self.on_keyup_callbacks = []
        self.button_switches_page = button_switches_page
        self.text = text or ''
        self.style = style


    @staticmethod
    def ensure_param_count(count=3):
        def wrapper(fn):
            try:
                signature = inspect.signature(fn)
            except:
                return fn

            @functools.wraps(fn)
            def wrapped(self, sd:StreamDeck, pressed:bool):
                kwargs = {'sd': sd, 'pressed': pressed}
                new_kwargs = dict()
                for key in signature.parameters:
                    if key in kwargs:
                        new_kwargs[key] = kwargs[key]
                if 'self' in kwargs:
                    new_kwargs['self'] = self
                return fn(**new_kwargs)
            return wrapped
        return wrapper

    def handle_button_event(self, pressed: bool):
        self.pressed = pressed
        callbacks = self.on_keydown_callbacks if pressed else self.on_keyup_callbacks

        # pressed a button that doesn't changes pages, so darken the background
        # print(f"just_pressed: {just_pressed}; self.button_switches_page: {self.button_switches_page}")
        if pressed and not self.button_switches_page:
            print("changing background color")
            self.set(background_color=self.style.pressed_background_color)
        # reset the button background color to regular button color
        else:
            self.set(background_color=self.style.background_color)

        for callback in callbacks:
            # print("calling callback:", callback)
            callback()

    def __call__(self, *args, **kwargs):
        # print(args, kwargs)
        return self.fn(*args, **kwargs)

    def set_slot(self, slot:'ButtonSlot'):
        self.slot = slot

    def set(
        self, fn=None, name=None,
        text=None, text_color=None, font_size=None,
        background_color=None,
        button_switches_page=None,
    ):
        if fn is not None:
            #TODO:any other linking we need to do here if we're attached to a board?.. or did our architecture cover that scenario?
            self.fn = self.ensure_param_count()(fn)
        if name is not None:
            self.name = name
        if button_switches_page is not None:
            self.button_switches_page = button_switches_page

        if text is not None:
            self.text = text
        if background_color is not None:
            self.background_color = background_color
        if text_color is not None:
            self.style.text_color = text_color
        if font_size is not None:
            self.style.font_size = font_size

        button_changed = bool(list(filter(None, [text, background_color, text_color, font_size])))
        if button_changed:
            self.alert_slot_button_changed()

    def alert_slot_button_changed(self):
        if self.slot is not None:
            self.slot.alert_button_changed()

    def set_image(self, index:int, sd:StreamDeck):
        if self.button_switches_page or not self.pressed:
            background_color = self.style.background_color
        # elif self.pressed:
        else:
            background_color = self.style.pressed_background_color
        sd.set_key_image(
            index,
            generate_text_image(
                background_color,
                self.style,
                self.text,
            ),
        )

    def reset(
        self,
        fn=None, name=None,
        text='',
        background_color=None,
        text_color=None,
        font_size=None,
    ):
        background_color = background_color or ButtonStyle.background_color
        text_color = text_color or ButtonStyle.text_color
        font_size = font_size or ButtonStyle.font_size

        self.set(
            fn=fn, name=name, text=text,
            background_color=background_color, text_color=text_color,
            font_size=font_size
        )

    def clear_slot(self):
        self.slot = None


class ButtonSlot:
    index:int
    button:Button
    sd: StreamDeck
    def __init__(self, index:int, sd:StreamDeck):
        self.index = index
        self.button = Button()
        self.sd = sd

    def set_button(self, button:Button):
        if self.button is not None:
            self.button.clear_slot()
        self.button = button
        self.button.set_slot(self)
        self.button.set_image(self.index, self.sd)

    def alert_button_changed(self):
        if self.button is not None:

            self.button.set_image(self.index, self.sd)

    def set_image(self):
        self.button.set_image(self.index, self.sd)
