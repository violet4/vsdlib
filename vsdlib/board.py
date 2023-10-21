import time
from typing import Dict, Optional, Tuple, Callable, List, Type

# here's a change to test poetry update..
# from PyQt5.QtWidgets import QApplication, QWidget

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck

from .button_style import ButtonStyle
from .buttons import Button, ButtonSlot
from .colors import black, reds, blues, greens, grays

def retry(max_count=20, seconds=1):
    """
    if stream deck is started at login, the process that starts it may not have
    full access to the system yet including the windowing system. this allows
    it to try for a while without permanently failing.
    """
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            count = 0
            while count < max_count:
                count += 1
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    print(e)
                    time.sleep(seconds)
            print(f"Failed after {max_count} tries with {seconds} seconds between each try..")
        return wrapped
    return wrapper


class BoardLayout:
    positions: Dict[int, Button]
    width: int
    key_count: int
    _initialized: bool = False

    @classmethod
    def initialize(cls, board:'Board'):
        cls._initialized = True
        cls.height = board.height
        cls.width = board.width
        cls.key_count = board.key_count
        cls.board = board

    @classmethod
    def _check_initialized(cls):
        if not cls._initialized:
            raise Exception("BoardLayout must be initialized before use")

    def __init__(self):
        self._check_initialized()
        self.positions = {
            i: Button()
            for i in range(self.key_count)
        }

    def set(self, button:Button, x, y=None):
        index = self.calc_index(x, y)
        self.positions[index] = button

    def refresh(self):
        if self.board.active_board_layout is self:
            self.board.apply(self)

    def calc_index(self, x, y=None):
        return x if y is None else y*self.width+x

    def apply(self, board:'Board'):
        board.apply(self)

    def create_return_button(self, board:'Board', text:str='< Back', style:ButtonStyle=ButtonStyle()):
        def handle_return_button_press(pressed:bool, *args, **kwargs):
            if pressed:
                self.apply(board)

        button = Button(handle_return_button_press, text=text, style=style, button_switches_page=True)
        return button

    def sublayout(
        self, board:'Board',
        to_text:str="Page",
        board_class:Optional[Type['BoardLayout']]=None,
        board_layout:Optional['BoardLayout']=None,
        return_text:str="< Back", style:ButtonStyle=ButtonStyle()
    ):
        return_button: Button = self.create_return_button(board, return_text)

        if board_layout is not None:
            new_layout = board_layout
        else:
            board_class = board_class or BoardLayout
            new_layout = board_class()

        new_layout.set(return_button, 0)
        new_page_button = new_layout.create_return_button(board, to_text, style=style)
        return new_layout, new_page_button, return_button


class Board:
    brightness: int
    buttons: Dict[int, Button]
    slots: Dict[int, ButtonSlot]
    key_count: int
    sd: StreamDeck
    _width: int
    _height: int
    timers: Dict[int, float]
    display_keys: Dict[str, int]
    dm: DeviceManager
    default_button_name: Optional[str] = None
    shutdown: bool = False
    debug_button: Button
    debug: bool

    background_color: str
    default_button_style: ButtonStyle = ButtonStyle()

    # app: QApplication
    active_board_layout: Optional[BoardLayout]

    def __init__(
        self, sd:Optional[StreamDeck]=None, dm:Optional[DeviceManager]=None,
    ):
        self.brightness = 30
        self.timers = dict()
        self.display_keys = dict()
        self.debug_button = Button(self._switch_debug, text='Debug', style=ButtonStyle(**grays))
        self.debug = False

        if sd is not None and dm is not None:
            self.sd = sd
            self.dm = dm
        else:
            self.dm = DeviceManager()
            self.sd: StreamDeck = self.dm.enumerate()[0]
            self.sd.open()

            self.sd.set_brightness = retry(10)(self.sd.set_brightness)
            self.sd.set_brightness(self.brightness)

        self.key_count = self.sd.key_count()
        self.size = self.sd.key_image_format()['size']
        ButtonStyle.set_size(self.size)
        self._width = self.sd.KEY_COLS
        self._height = self.key_count//self.sd.KEY_COLS
        self.active_board_layout = None

        self.slots = {
            i: ButtonSlot(i, self.sd)
            for i in range(self.sd.key_count())
        }

        self.sd.set_key_callback_async(self.handle_key_event)
        # self.sd.set_key_callback(self.handle_key_event)
        # self.app = QApplication([])

    def _switch_debug(self, pressed:bool):
        if not pressed:
            return
        self.debug = not self.debug
        print("self.debug switched to", self.debug)
        self.debug_button.set(**(greens if self.debug else grays))
        # self.debug_button.alert_slot_button_changed()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def calc_index(self, x, y=None):
        return x if y is None else y*self.width+x

    def get(self, x, y=None):
        index = self.calc_index(x, y)
        return self.buttons[index]

    def set_button(
        self, x, y=None, fn:Optional[Callable]=None, name:Optional[str]=None,
        text:Optional[str]=None,
        text_color:str=black, font_size:int=40,
        background_color=None,
        button_switches_page=None,
    ):
        index = self.calc_index(x, y)
        button: Button = self.buttons[index]

        button.set(fn, name, text, text_color, font_size,
                   background_color,
                   button_switches_page)

    def unset_display_key(self, name:str):
        index = self.display_keys[name]
        self.buttons[index].reset()
        del self.display_keys[name]

    async def handle_key_event(self, sd:StreamDeck, index:int, pressed:bool):
    # def handle_key_event(self, sd:StreamDeck, index:int, pressed:bool):
        button = self.buttons[index]
        if pressed:
            self.timers[index] = time.time()
        elif index in self.timers:
            print(time.time()-self.timers[index])

        # if pressed and self.debug:
        #     try:
        #         import ipdb; ipdb.set_trace()
        #     except ImportError:
        #         pass

        button.handle_button_event(pressed)
        button(sd, index, pressed)

    # async def handle_key_event(*args, **kwargs):
    #     print("handle_key_event", args, kwargs)


    def close(self):
        self.sd.close()

    def apply(self, layout:BoardLayout):
        self.active_board_layout = layout
        self.buttons = layout.positions
        for i in self.buttons.keys():
            self.slots[i].set_button(self.buttons[i])
        # for index, button in layout.positions.items():
        #     self.buttons[index] = button
        # self.sd.set_key_callback(self.handle_key_event)

    def sub_board(self):
        return Board(self.sd, self.dm)


class SubLayout(BoardLayout):
    def __init__(
        self, board_name:str, board:Board, from_layout:BoardLayout,
        button_style:ButtonStyle=ButtonStyle(**blues),
    ):
        super().__init__()
        new_layout, button, return_button = from_layout.sublayout(
            board, board_name, style=button_style
        )
        self.layout = new_layout
        self.button = button
        self.return_button = return_button
