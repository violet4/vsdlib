import os
import time


from vsdlib.widgets import CalculatorWidget
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
        super().__init__("Positions", board, from_layout)
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
        super().__init__("Alphabet", board, from_layout)

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
