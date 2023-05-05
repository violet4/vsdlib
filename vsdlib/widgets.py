from typing import Dict, Optional, Tuple, Callable, List
import subprocess

from .board import Board
from .buttons import Button
from .button_style import ButtonStyle
from .colors import grays

class Widget:
    board: Board
    style: ButtonStyle
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        self.board = board
        self.style = style


class VolumeWidget(Widget):
    increase_volume_button: Button
    decrease_volume_button: Button
    display_volume_button: Button
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, style)
        self.display_volume_button = Button(text=self.get_current_volume(), style=style)
        self.increase_volume_button = Button(
            self.create_change_volume_fn(self.display_volume_button),
            text="Vol+", style=style
        )
        self.decrease_volume_button = Button(
            self.create_change_volume_fn(self.display_volume_button, decrease=True),
            text="Vol-", style=style
        )

    @staticmethod
    def create_change_volume_fn(display_volume_button:Button, decrease:bool=False):
        def change_volume(pressed):
            if not pressed:
                return
            char = '-' if decrease else '+'
            new_val = subprocess.check_output(
                f"amixer set 'Master' 5%{char} | grep Right --color=never | tail -1|cut -d'[' -f2|cut -d']' -f1",
                shell=True,
            ).decode().strip()
            display_volume_button.set(text=new_val)
        return change_volume

    @staticmethod
    def get_current_volume():
        return subprocess.check_output(
            f"amixer set 'Master' 0%- | grep Right --color=never | tail -1|cut -d'[' -f2|cut -d']' -f1",
            shell=True,
        ).decode().strip()


class BrightnessWidget(Widget):
    brightness_display_button: Button
    brightness_up_button: Button
    brightness_down_button: Button

    _min_brightness:int = 10
    _max_brightness:int = 100

    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, style)
        self.brightness_display_button = Button(text=str(self.board.brightness), style=style)
        self.brightness_up_button = Button(
            self.make_change_brightness_down_callback(self.brightness_display_button),
            text='Lite-', style=style,
        )
        self.brightness_down_button = Button(
            self.make_change_brightness_up_callback(self.brightness_display_button),
            text='Lite+', style=style,
        )

    def get_brightness(self):
        return self.board.brightness

    def make_change_brightness_callback(self, brightness_display_button:Button, diff:int):
        def change_brightness(pressed:bool):
            if pressed:
                new_brightness = self.change_brightness(diff)
                brightness_display_button.set(text=str(new_brightness))
        return change_brightness

    def change_brightness(self, diff: int):

        self.board.brightness += diff
        if self.board.brightness < self._min_brightness:
            self.board.brightness = self._min_brightness
        elif self.board.brightness > self._max_brightness:
            self.board.brightness = self._max_brightness
        self.board.sd.set_brightness(self.board.brightness)
        return self.board.brightness

    def make_change_brightness_up_callback(self, brightness_display_button:Button):
        return self.make_change_brightness_callback(brightness_display_button, 10)

    def make_change_brightness_down_callback(self, brightness_display_button:Button):
        return self.make_change_brightness_callback(brightness_display_button, -10)


class NumPadWidget(Widget):
    number_buttons: Dict[int, Button]
    entries: List
    spool_display_widget: Button
    bvalue: Button
    def __init__(self, board:Board, style:ButtonStyle):
        self.entries = []
        self.number_buttons: Dict[int, Button] = dict()
        self.spool_display_widget = Button(text='0', style=style)
        self.bvalue = Button(text='0', style=style)
        for i in range(10):
            self.number_buttons[i] = Button(self.create_number_button_callback(i), text=str(i), style=style)

    def create_number_button_callback(self, number:int):
        def press_number_button(pressed:bool):
            if not pressed:
                return
            self.entries.append(number)
            joined = self.get_joined()
            self.spool_display_widget.set(text=joined)
            self.bvalue.set(text=f'{eval(joined):.2f}')
            try:
                self.bvalue.set(text=f'{eval(joined):.2f}')
            except:
                print(f"failed to evaluate: '{joined}'")
                self.bvalue.set(text=joined)
        return press_number_button

    def get_joined(self):
        return ''.join(str(v) for v in self.entries)


class CalculatorWidget(NumPadWidget):
    #TODO:merge to a number_buttons list and index by the number you want, e.g. number_buttons[0] will be the 0 button.
    bplus: Button
    bminus: Button
    bequals: Button
    bmult: Button
    bdiv: Button
    bbackspace: Button
    result_style = ButtonStyle(background_color='#37d495', pressed_background_color='#297858')
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, self.result_style)

        self.bdecimal = Button(self.create_operation_button_callback('.'), text='.', style=style)

        operator_style = ButtonStyle(**grays)
        self.bplus = Button(self.create_operation_button_callback('+'), text='+', style=operator_style)
        self.bminus = Button(self.create_operation_button_callback('-'), text='-', style=operator_style)
        self.bmult = Button(self.create_operation_button_callback('*'), text='*', style=operator_style)
        self.bdiv = Button(self.create_operation_button_callback('/'), text='/', style=operator_style)
        self.bequals = Button(self.create_equals_button_callback(), text='=', style=operator_style)
        self.bbackspace = Button(self.create_backspace_button_callback(), text='<', style=operator_style)
        self.bclear = Button(self.create_clear_button_callback(), text='Clr', style=operator_style)

    def create_clear_button_callback(self):
        def perform_clear(pressed:bool):
            if not pressed:
                return
            self.entries.clear()
            print("setting spool display to ''")
            self.spool_display_widget.set(text='')
            # self.spool_display_widget.alert_slot_button_changed()
            print("setting value display to ''")
            self.bvalue.set(text='')
            # self.bvalue.alert_slot_button_changed()
        return perform_clear

    def create_backspace_button_callback(self):
        def perform_backspace(pressed:bool):
            if not pressed:
                return
            try:
                self.entries.pop()
                joined = self.get_joined()
                self.spool_display_widget.set(text=joined)
                try:
                    self.bvalue.set(text=f"{eval(joined):.2f}")
                except:
                    self.bvalue.set(text=joined)
            except:
                pass
        return perform_backspace

    def create_equals_button_callback(self):
        def perform_equals(pressed:bool):
            if not pressed:
                return
            try:
                joined = self.get_joined()
                newval = f'{eval(joined):.2f}'
                self.entries = [c for c in newval]
                self.spool_display_widget.set(text=newval)
                self.bvalue.set(text=newval)
            except:
                pass
        return perform_equals

    def create_operation_button_callback(self, operation:str):
        def perform_operation(pressed:bool):
            if not pressed:
                return
            self.entries.append(operation)
            joined = self.get_joined()
            self.spool_display_widget.set(text=joined)
            try:
                value = f'{eval(joined):.2f}'
            except:
                value = joined
            self.bvalue.set(text=value)

        return perform_operation


class TimerWidget(NumPadWidget):
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, style)
        self.soonest_countdown_button = Button()
        button: Button
        for i, button in self.number_buttons.items():
            button.fn = self.create_push_button_callback(button.fn, i)
        # self. = Button()

    def create_push_button_callback(self, button, i):
        def new_number_button(pressed:bool):
            if not pressed:
                return
            print("pushed a number button", i)
            button(pressed)
        return new_number_button



