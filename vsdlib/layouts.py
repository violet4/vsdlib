import threading
import time

from vsdlib.widgets import CalculatorWidget, BluetoothWidget, KeyPadWidget, ListWidget, VSCodeWidget
from vsdlib.board import Board, BoardLayout
from vsdlib.buttons import Button, ButtonStyle
from vsdlib.colors import reds, oranges, yellows, greens, blues, purples, black, pinks, indigos, violets
from vsdlib.images import get_asset_path


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


class TimerLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Timer", board, from_layout)

vscode_image_path = get_asset_path('vscode.jpg')

class CalcLayout(SubLayout):
    calcwid: CalculatorWidget
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__(
            "Calc", board, from_layout,
            button_style=ButtonStyle(image_path=get_asset_path('calculator.jpg')),
        )
        self.calcwid = CalculatorWidget(board)

        spool_display_widget = self.calcwid.spool_display_widget
        bvalue = self.calcwid.bvalue
        bplus = self.calcwid.bplus
        bminus = self.calcwid.bminus
        bequals = self.calcwid.bequals
        bmult = self.calcwid.bmult
        bdiv = self.calcwid.bdiv
        bbackspace = self.calcwid.bbackspace
        bdecimal = self.calcwid.bdecimal
        bclear = self.calcwid.bclear
        pleft = self.calcwid.pleft
        pright = self.calcwid.pright

        for x in range(1,3+1,1):
            for y in range(1,3+1,1):
                self.layout.set(self.calcwid.number_buttons[y+(x-1)*3], x, y)
        self.layout.set(self.calcwid.number_buttons[0], 0,2)

        # parens exponent multiply divide add subtract

        self.layout.set(bequals, 0,3)

        self.layout.set(bdiv, 4,0)
        self.layout.set(bminus, 3,0)
        self.layout.set(bplus, 2,0)
        self.layout.set(bmult, 1,0)
        self.layout.set(bdecimal, 0,1)


        self.layout.set(spool_display_widget, 5,1)
        self.layout.set(bvalue, 4,1)

        self.layout.set(pleft, 4,2)
        self.layout.set(pright, 4,3)

        self.layout.set(bbackspace, 5,3)
        self.layout.set(bclear, 5,2)


class PositionLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Posi\ntions", board, from_layout)
        for x in range(board.width):
            for y in range(board.height):
                if x+y == 0:
                    continue
                if self.layout.calc_index(x,y) == self.key_count-1:
                    text = f"{x}, {y}\nwidth={board.width}\nheight={board.height}"
                else:
                    text = f"{x},{y}"
                self.layout.set(Button(text=text), x,y)


class AlphabetLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Alpha\nbet", board, from_layout)

        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        i = 0
        cg = self.color_generator()
        for y in range(4):
            for x in range(1, 7+1):
                char = alphabet[i]
                self.layout.set(Button(text=char, style=ButtonStyle(**next(cg))), x, y)
                i += 1
                if i >= len(alphabet):
                    break
            if i >= len(alphabet):
                break

    @staticmethod
    def color_generator():
        while True:
            for color in (reds, oranges, yellows, greens, blues, indigos, violets):
                yield color


class BluetoothLayout(SubLayout):
    _thread: threading.Thread
    _thread_quit: bool
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Btooth", board, from_layout, button_style=ButtonStyle(image_path=get_asset_path('bluetooth.jpg')))
        self.bluewid = BluetoothWidget(board, style=ButtonStyle(**blues))
        self.button.fn = self.wrap_button_refresh(self.button.fn)
        self._thread: threading.Thread
        self._thread_quit = False
        self.return_button = self.stop_refresh_on_return(self.return_button)

    @staticmethod
    def stop_refresh_on_return(fn):
        def wrapper(self, *args, **kwargs):
            self._thread_quit = True
            return fn(*args, **kwargs)
        return wrapper

    def continuous_refresh_btooth(self):
        while not self._thread_quit:
            self.refresh()
            time.sleep(1)

    def start_refresh_thread(self):
        self._thread = threading.Thread(
            target=self.continuous_refresh_btooth, args=(self,), daemon=True
        )
        self._thread.start()

    def wrap_button_refresh(self, fn):
        def wrapped(*args, **kwargs):
            self.refresh()
            return fn(*args, **kwargs)
        return wrapped

    def refresh(self):
        self.bluewid.refresh()
        for i, button in enumerate(self.bluewid.buttons):
            self.layout.set(button, i+1)


class RecurringTasksLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Recur\nTasks", board, from_layout)
        #TODO:self=self.layout .. not separate field..
        self.widget = ListWidget(self.layout, board)
        self.layout.set(self.widget.new_task_button, 1)


class MedTrackerLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Med\nTracking", board, from_layout)
        #TODO:self=self.layout .. not separate field..
        self.widget = ListWidget(self.layout, board)
        self.layout.set(self.widget.new_task_button, 1)


class VSCodeLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("VSCode", board, from_layout, button_style=ButtonStyle(image_path=get_asset_path('vscode.jpg')))
        self.widget = VSCodeWidget(board)
        self.layout.set(self.widget.vscode, 3,1)

        self.layout.set(self.widget.dashboard, 3,0)
        self.layout.set(self.widget.vsdlib, 3,2)


class NumpadLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Num\npad", board, from_layout)

        self.widget = KeyPadWidget(board, style=ButtonStyle(), strings=[str(i) for i in range(10)])

        self.layout.set(self.widget.button_dict['0'], 4,3)

        self.layout.set(self.widget.button_dict['1'], 3,2)
        self.layout.set(self.widget.button_dict['2'], 4,2)
        self.layout.set(self.widget.button_dict['3'], 5,2)
        self.layout.set(self.widget.button_dict['4'], 3,1)
        self.layout.set(self.widget.button_dict['5'], 4,1)
        self.layout.set(self.widget.button_dict['6'], 5,1)
        self.layout.set(self.widget.button_dict['7'], 3,0)
        self.layout.set(self.widget.button_dict['8'], 4,0)
        self.layout.set(self.widget.button_dict['9'], 5,0)

        self.layout.set(self.widget.backspace_button, 7,0)
        self.layout.set(self.widget.up_button, 6,2)
        self.layout.set(self.widget.space_button, 7,2)
        self.layout.set(self.widget.down_button, 6,3)
        self.layout.set(self.widget.left_button, 5,3)
        self.layout.set(self.widget.right_button, 7,3)
        self.layout.set(self.widget.enter_button, 7,1)


class EmojiPadLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Emoji\npad", board, from_layout)
        self.widget = KeyPadWidget(board)
        # 💜
        self.layout.set(self.widget.add_emoji_button('\u1F60D', '\u1F60'), 7,1)


class aTimeLoggerLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("a\nTime\nLogger", board, from_layout)


class NotesLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Notes", board, from_layout)
