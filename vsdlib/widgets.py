from typing import Dict, Optional, List
import subprocess
import time
import threading
import datetime

from vsdlib.board import Board
from vsdlib.buttons import Button, EmojiButton
from vsdlib.button_style import ButtonStyle
from vsdlib.colors import grays, greens, blues, reds, pinks, whites


class Widget:
    board: Board
    style: ButtonStyle
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        self.board = board
        self.style = style


from contextlib import contextmanager


def get_window_by_name(search_str:str):
    return subprocess.check_output(['xdotool', 'search', '--onlyvisible', '--class', search_str]).decode().strip()


@contextmanager
def activate_window(search_str:str):
    """
    search_str e.g. 'discord'
    """
    previous_window_id:str = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
    new_active_window_id:str = get_window_by_name(search_str)

    subprocess.call(['xdotool', 'windowactivate', new_active_window_id])
    yield
    subprocess.call(['xdotool', 'windowactivate', previous_window_id])


def send_hotkey(hotkey_str:str):
    subprocess.call(['xdotool', 'key', hotkey_str])


class DiscordWidget(Widget):
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle(**pinks)):
        super().__init__(board, style)
        self.toggle_mute_button = Button(self.create_send_mute_keystroke_button(), text='Discord\nToggle\nMute', style=style)
        self.muted = False

    def create_send_mute_keystroke_button(self):
        def send_mute_keystroke(pressed:bool):
            if not pressed:
                return
            with activate_window('discord'):
                send_hotkey('ctrl+shift+m')
            self.muted = not self.muted
            self.toggle_mute_button.set(text='Discord\n(Muted)' if self.muted else 'Discord\nUnmuted')
        return send_mute_keystroke


class ClockWidget(Widget):
    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle(**whites)):
        super().__init__(board, style)
        self.clock_button = Button(lambda *args, **kwargs: None, style=style)
        self.clock_thread = threading.Thread(target=self.keep_clock_updated, daemon=True)
        self.clock_thread.start()

    def keep_clock_updated(self):
        dow_lookup = {
            0: 'M',
            1: 'T',
            2: 'W',
            3: 'R',
            4: 'F',
            5: 'S',
            6: 'U',
        }
        while True:
            now = datetime.datetime.now()
            dow = dow_lookup[now.weekday()]
            self.clock_button.set(text=now.strftime(
                f'%H:%M:%S\n'      # 8
                f' %m-%d{dow}\n'   # 6
                f'  %Y'            # 4
            ))
            time.sleep(1)


def create_try_playerctl_command(command:str='play-pause'):
    def try_playerctl_command(pressed:bool):
        if not pressed:
            return
        try:
            subprocess.call(['playerctl', command])
        except Exception as e:
            pass
    return try_playerctl_command


playpause = create_try_playerctl_command()
prevtrack = create_try_playerctl_command('previous')
nexttrack = create_try_playerctl_command('next')


class MediaControlWidget(Widget):
    def __init__(self):
        bs = ButtonStyle(**greens)
        self.prevtrack = Button(prevtrack, text='<', style=bs)
        self.playpause = Button(playpause, text='>||', style=bs)
        self.nexttrack = Button(nexttrack, text='>', style=bs)


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
            # type the string out.. what library?
        return press_number_button

    def create_press_callback(self, string:str):
        def press_number_button(pressed:bool):
            if not pressed:
                return
            # type the string out.. what library?
        return press_number_button


class NumPadWidget(Widget):
    number_buttons: Dict[int, Button]
    entries: List
    spool_display_widget: Button
    bvalue: Button
    def __init__(self, board:Board, style:ButtonStyle):
        self.entries = []
        self.number_buttons: Dict[int, Button] = dict()
        self.spool_display_widget = Button(text='0')#, style=style)
        self.bvalue = Button(text='0')#, style=style)
        for i in range(10):
            self.number_buttons[i] = Button(self.create_number_button_callback(i), text=str(i))#, style=style)

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


class VSCodeWidget(Widget):
    vsdlib: Button
    dashboard: Button
    some_style = ButtonStyle(background_color='#37d495', pressed_background_color='#297858')

    def __init__(self, board:Board, style:ButtonStyle=ButtonStyle()):
        super().__init__(board, self.some_style)

        self.vscode = Button(self.create_vscode_button_callback(), text='VSCode', style=ButtonStyle(**blues))
        self.vsdlib = Button(self.create_vscode_button_callback('/home/violet/git/violet/vsdlib'), text='Stream\nDeck', style=style)
        self.dashboard = Button(self.create_vscode_button_callback('/home/violet/git/violet/dashboard'), text='Web\nDashboard', style=style)

    def create_vscode_button_callback(self, directory:Optional[str]=None):
        def vscode_dir(pressed:bool):
            if not pressed:
                return
            args = ['/usr/bin/code', '--vmodule="*/components/os_crypt/*=1"']
            if directory is not None:
                args.append(directory)
            cmd = ' '.join(args)
            cmd = f'pwd; nohup bash -c {cmd} >> nohup_vscode.txt &'
            subprocess.call(cmd, shell=True)
        return vscode_dir


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
        # super().__init__(board, self.result_style)
        super().__init__(board, style)

        operator_style = ButtonStyle(**grays)
        self.bdecimal = Button(self.create_operation_button_callback('.'), text='.', style=operator_style)

        self.pleft = Button(self.create_operation_button_callback('('), text='(', style=operator_style)
        self.pright = Button(self.create_operation_button_callback(')'), text=')', style=operator_style)

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
    _thread: threading.Thread

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
