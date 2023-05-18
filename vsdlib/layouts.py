from vsdlib.widgets import CalculatorWidget, BluetoothWidget, KeyPadWidget, ListWidget
from vsdlib.board import Board, BoardLayout
from vsdlib.buttons import Button, ButtonStyle
from vsdlib.colors import reds, oranges, yellows, greens, blues, purples, black, pinks, indigos, violets


class SubLayout(BoardLayout):
    def __init__(self, board_name:str, board:Board, from_layout:BoardLayout):
        super().__init__()
        new_layout, button = from_layout.sublayout(board, board_name, style=ButtonStyle(**blues))
        self.layout = new_layout
        self.button = button


class TimerLayout(SubLayout):
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Timer", board, from_layout)


class CalcLayout(SubLayout):
    calcwid: CalculatorWidget
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Calc", board, from_layout)
        self.calcwid = CalculatorWidget(board, style=ButtonStyle(**greens))

        i = 1
        for y in range(2, 0-1, -1):
            for x in range(board.width-3, board.width):
                self.layout.set(self.calcwid.number_buttons[i], x, y)
                i += 1
                if i == 10:
                    i = 0
        self.layout.set(self.calcwid.number_buttons[i], 6, 3)

        self.layout.set(self.calcwid.spool_display_widget, 4,0)
        self.layout.set(self.calcwid.bvalue, 4,1)

        self.layout.set(self.calcwid.bplus, 0,1)
        self.layout.set(self.calcwid.bminus, 0,2)
        self.layout.set(self.calcwid.bequals, 7,3)
        self.layout.set(self.calcwid.bmult, 1,1)
        self.layout.set(self.calcwid.bdiv, 1,2)
        self.layout.set(self.calcwid.bbackspace, 4,3)
        self.layout.set(self.calcwid.bdecimal, 5,3)
        self.layout.set(self.calcwid.bclear, 4,2)


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
    def __init__(self, board:Board, from_layout:BoardLayout):
        super().__init__("Blue\ntooth", board, from_layout)
        self.bluewid = BluetoothWidget(board, style=ButtonStyle(**blues))
        self.button.fn = self.wrap_button_refresh(self.button.fn)

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
