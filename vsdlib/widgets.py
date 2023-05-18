from typing import Dict, Optional, Tuple, Callable, List
import subprocess

import pyautogui as pag
import pyautogui

from .board import Board, BoardLayout
from .buttons import Button, EmojiButton
from .button_style import ButtonStyle
from .colors import grays, greens, blues, reds
from .contrib.todos import Todo, Session

pyautogui._pyautogui_x11.keyboardMapping['prevtrack']=173 # type: ignore
pyautogui._pyautogui_x11.keyboardMapping['playpause']=172 # type: ignore
pyautogui._pyautogui_x11.keyboardMapping['nexttrack']=171 # type: ignore


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
    muted: bool
    volume: str
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, style)
        self.volume = self.get_current_volume()
        self.muted = self.is_muted()
        self.display_volume_button = Button(self.create_mute_fn(), style=style)
        self.set_volume_str()
        self.increase_volume_button = Button(
            self.create_change_volume_fn(self.display_volume_button),
            text="Vol+", style=style
        )
        self.decrease_volume_button = Button(
            self.create_change_volume_fn(self.display_volume_button, decrease=True),
            text="Vol-", style=style
        )

    def set_volume_str(self):
        volume = self.get_current_volume()
        muted = self.muted
        text = f'muted\n({volume})' if muted else volume
        self.display_volume_button.set(text=text)

    def create_mute_fn(self):
        def toggle_mute(pressed):
            if not pressed:
                return
            subprocess.check_output(
                "amixer set 'Master' {}mute".format('un' if self.muted else ''),
                shell=True,
            )
            self.muted = not self.muted
            self.set_volume_str()
        return toggle_mute


    def create_change_volume_fn(self, display_volume_button:Button, decrease:bool=False):
        def change_volume(pressed):
            if not pressed:
                return
            char = '-' if decrease else '+'
            subprocess.check_output(
                f"amixer set 'Master' 5%{char} | grep Right --color=never | tail -1|cut -d'[' -f2|cut -d']' -f1",
                shell=True,
            ).decode().strip()
            self.set_volume_str()
        return change_volume

    @staticmethod
    def is_muted():
        value = subprocess.check_output(
            f"amixer set 'Master' 0%- | grep Right --color=never | tail -1",
            shell=True,
        ).decode().strip()
        return '[off]' in value

    @staticmethod
    def get_current_volume():
        value = subprocess.check_output(
            f"amixer set 'Master' 0%- | grep Right --color=never | tail -1",
            shell=True,
        ).decode().strip()
        return value.split('[')[1].split(']')[0]


class MediaControlWidget(Widget):
    def __init__(self):
        self.prevtrack = Button(lambda pressed: pyautogui.press('prevtrack') if pressed else None, text='<')
        self.playpause = Button(lambda pressed: pyautogui.press('playpause') if pressed else None, text='>||')
        self.nexttrack = Button(lambda pressed: pyautogui.press('nexttrack') if pressed else None, text='>')


class BrightnessWidget(Widget):
    brightness_display_button: Button
    brightness_up_button: Button
    brightness_down_button: Button

    _min_brightness:int = 10
    _max_brightness:int = 100

    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, style)
        self.brightness_display_button = Button(style=style)
        self.set_brightness_str()
        self.brightness_up_button = Button(
            self.make_change_brightness_down_callback(),
            text='Lite-', style=style,
        )
        self.brightness_down_button = Button(
            self.make_change_brightness_up_callback(),
            text='Lite+', style=style,
        )

    def set_brightness_str(self):
        self.brightness_display_button.set(text=f'{self.board.brightness}\nTODO\nsleep\nmode')

    def get_brightness(self):
        return self.board.brightness

    def make_change_brightness_callback(self, diff:int):
        def change_brightness(pressed:bool):
            if pressed:
                self.change_brightness(diff)
                self.set_brightness_str()
        return change_brightness

    def change_brightness(self, diff: int):

        self.board.brightness += diff
        if self.board.brightness < self._min_brightness:
            self.board.brightness = self._min_brightness
        elif self.board.brightness > self._max_brightness:
            self.board.brightness = self._max_brightness
        self.board.sd.set_brightness(self.board.brightness)
        return self.board.brightness

    def make_change_brightness_up_callback(self):
        return self.make_change_brightness_callback(10)

    def make_change_brightness_down_callback(self):
        return self.make_change_brightness_callback(-10)


class KeyPadWidget(Widget):
    """
    A list of keys that, when typed, enter the value pressed.
    e.g. for a calculator or numpad.
    """
    buttons: List[Button]
    button_dict: Dict[str, Button]
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle(), strings:Optional[List[str]]=None):
        super().__init__(board, style)
        self.buttons: List[Button] = []
        self.button_dict = dict()

        self.backspace_button = Button(self.create_press_callback('backspace'), text='<=')
        self.up_button = Button(self.create_press_callback('up'), text='^')
        self.down_button = Button(self.create_press_callback('down'), text='v')
        self.left_button = Button(self.create_press_callback('left'), text='<')
        self.right_button = Button(self.create_press_callback('right'), text='>')

        self.space_button = Button(self.create_press_callback(' '), text=',_,')
        self.enter_button = Button(self.create_press_callback('enter'), text='\\n')

        if strings is None:
            strings = []
        for s in strings:
            button: Button = Button(self.create_press_callback(s), text=s, style=style)
            self.button_dict[s] = button
            self.buttons.append(button)

    def add_button(self, button_text:str, type_text:str):
        button: Button = Button(self.create_typewrite_callback(type_text), text=button_text)
        self.buttons.append(button)
        self.button_dict[button_text] = button
        return button

    def add_emoji_button(self, button_text:str, type_text:str):
        button: Button = EmojiButton(self.create_typewrite_callback(type_text), text=button_text)
        self.buttons.append(button)
        self.button_dict[button_text] = button
        return button

    def create_typewrite_callback(self, string:str):
        def press_number_button(pressed:bool):
            if not pressed:
                return
            pag.typewrite(string)
        return press_number_button

    def create_press_callback(self, string:str):
        def press_number_button(pressed:bool):
            if not pressed:
                return
            pag.press(string)
        return press_number_button


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


def check_device_connected(mac):
    connected = False
    lines = subprocess.check_output(['bluetoothctl', 'info', mac]).decode()
    for line in lines.split('\n'):
        if "Connected:" in line:
            connected = line.strip().split()[1]=='yes'
            break
    return connected


class BluetoothWidget(Widget):

    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, style)
        self.refresh()


    def refresh(self):
        lines = subprocess.check_output(['bluetoothctl', 'devices', 'Paired']).decode().strip().split('\n')
        self.devices = []
        self.buttons = []
        for line in lines:
            _, mac, name = line.split(maxsplit=2)
            self.devices.append((name, mac))
            connected = check_device_connected(mac)
            style = ButtonStyle(**(greens if connected else reds))
            button = Button(
                text=f'{name}\n({"" if connected else "not "}conn)',
                style=style,
            )
            toggle_connection_callback = self.generate_toggle_connection_callback(button, name, mac, connected)
            button.fn = toggle_connection_callback
            self.buttons.append(button)


    @staticmethod
    def generate_toggle_connection_callback(button:Button, name, mac, connected):
        def toggle_connection_wrapper(connected):
            connected = {'connected':connected}
            def toggle_connection(_, _2, pressed):
                if not pressed:
                    return
                if not connected['connected']:
                    button.style = ButtonStyle(**blues)
                    try:
                        lines = subprocess.check_output(['bluetoothctl', 'connect', mac]).decode()
                        now_connected = 'Connection successful' in lines
                    except:
                        now_connected = False
                    if now_connected:
                        connected['connected'] = True
                        button.style = ButtonStyle(**greens)
                        button.set(text=f'{name}\n(conn)')

                else:
                    button.set(background_color=blues['background_color'])
                    button.style = ButtonStyle(**blues)
                    try:
                        lines = subprocess.check_output(['bluetoothctl', 'disconnect', mac]).decode()
                        disconnected = 'Successful disconnected' in lines
                    except:
                        disconnected = True
                    if disconnected:
                        connected['connected'] = False
                        button.style = ButtonStyle(**reds)
                        button.set(text=f'{name}\n(not conn)')
            return toggle_connection

        return toggle_connection_wrapper(connected)


from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QPlainTextEdit

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QShortcut, QApplication, QMessageBox

from PyQt5.QtWidgets import QApplication,QWidget,QTextEdit,QVBoxLayout,QPushButton

from PyQt5.QtGui import QKeySequence

class TextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('Text Input Dialog')
        self.input_label = QLabel('Enter your text:')
        self.text_input = QTextEdit()
        self.cancel_button = QPushButton('Cancel')
        self.submit_button = QPushButton('Submit')
        
        layout = QVBoxLayout()
        layout.addWidget(self.input_label)
        layout.addWidget(self.text_input)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)
        
        self.cancel_button.clicked.connect(self.reject)
        self.submit_button.clicked.connect(self.accept)
        
        self.submit_button.setDefault(True)
        
        # Create a shortcut for submitting the text input
        submit_shortcut = QShortcut(QKeySequence('Ctrl+Return'), self)
        submit_shortcut.activated.connect(self.submit)
        submit_shortcut = QShortcut(QKeySequence('Alt+Return'), self)
        submit_shortcut.activated.connect(self.submit)
        
    def submit(self):
        self.accept()
        
    def get_text(self):
        result = self.exec_()
        text = self.text_input.toPlainText() if result == QDialog.Accepted else None
        return text


def get_text_input(parent=None):
    dialog = TextInputDialog(parent)
    return dialog.get_text()


class ListWidget(Widget):
    new_task_button: Button
    layout: BoardLayout
    tasks: List[Button]
    task_id: int
    def __init__(self, layout:BoardLayout, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, style)
        self.layout = layout
        self.tasks = []

        # tasks = [
        #     'litter',
        #     'chx',
        #     'taters',
        #     'kitty\nwater',
        #     'moak\nstory\nfollowup',
        # ]
        with Session() as sess:
            todos: List[Todo] = sess.query(Todo).all()
            for todo in todos:
                self.add_task_button(int(todo.tid), str(todo.name), refresh=False)  # type: ignore

        self.layout.refresh()

        self.new_task_button = Button(
            self.create_add_task_callback(layout), text="+Task",
            style=ButtonStyle(**greens),
        )
        self.task_id = 0

    def redraw_layout(self):
        for i, task_button in enumerate(self.tasks):
            # print(f"setting {i+2} to {task_button.text}")
            self.layout.set(task_button, i+2)
        for j in range(len(self.tasks)+2, self.board.key_count):
            # print(f"setting {j} to empty button")
            # print(f"self.layout.set(Button(), j({j}))")
            self.layout.set(Button(), j)
        self.layout.refresh()

    def create_delete_task_handler(self, button:Button, task_id:int):
        def delete_task(_, _2, pressed:bool):
            if not pressed:
                return
            # print('before self.tasks.remove(button):', self.tasks)
            print(f"removing button: {button.text}")
            with Session() as sess:
                sess.query(Todo).where(Todo.tid==task_id).delete()
                sess.commit()

            self.tasks.remove(button)
            # print('after self.tasks.remove(button):', self.tasks)
            # print('before redraw_layout')
            # print([b.text for b in self.tasks])
            self.redraw_layout()
            # print('after redraw_layout')
        return delete_task

    def create_task_button(self, task_id:int, task_text:str, style:ButtonStyle=ButtonStyle(**blues)):
        button = Button(text=task_text, style=style)
        button.fn = self.create_delete_task_handler(button, task_id)
        return button

    def add_task_button(self, task_id:int, task_text:str, refresh:bool=True):
        new_task_button = self.create_task_button(task_id, task_text)
        self.tasks.append(new_task_button)
        self.layout.set(new_task_button, len(self.tasks)+1)
        if refresh:
            self.layout.refresh()

    def create_add_task_callback(self, layout:BoardLayout):
        def new_task_button(pressed:bool):
            if not pressed:
                return

            text = get_text_input()
            if text is not None:
                with Session() as sess:
                    todo = Todo(name=text)
                    sess.add(todo)
                    sess.commit()
                    self.add_task_button(int(todo.tid), text)  # type: ignore
        return new_task_button
