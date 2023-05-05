#!/usr/bin/env python3
"""
Button manages creating/producing pictures while Board manages index locations and setting the picture

TODO:
* board that makes it easier to remember what i want to code next - todo list
* numpad
* timer
* ..

"""
import os
import time


from vsdlib.widgets import VolumeWidget, BrightnessWidget, CalculatorWidget
from vsdlib.board import Board, BoardLayout
from vsdlib.buttons import Button, ButtonStyle
from vsdlib.colors import reds, oranges, yellows, greens, blues, purples, black, pinks, indigos, violets
from vsdlib.layouts import TimerLayout, CalcLayout, PositionLayout, AlphabetLayout


def create_restart_button(board:Board, style:ButtonStyle=ButtonStyle()):
    def restart_streamdeck():
        print("RESTARTING!!!!!!!")
        board.close()
        os.system('pipenv run python violetdeck.py')
        # self.shutdown = True
    button: Button = Button(
        restart_streamdeck,
        'restart',
        # '   ⏻   \n'
        'Restart',
        style=style,
    )
    return button


def run_main():
    """
    TODO:switch discord mic between scarlet and obsidian
    TODO:"off"/"dark" mode - brightness 0, all buttons become "wake up" buttons
    """
    board = Board()

    BoardLayout.initialize(board)

    main_layout = BoardLayout()
    # main_layout_button: Button = main_layout.create_return_button(board, "< Home")

    calc = CalcLayout(board, main_layout)
    position_layout = PositionLayout(board, main_layout)
    alphabet_layout = AlphabetLayout(board, main_layout)
    timer = TimerLayout(board, main_layout)

    # main page top bar
    main_layout.set(position_layout.button, 0)
    main_layout.set(calc.button, 1)
    main_layout.set(timer.button, 2)
    # ..
    main_layout.set(alphabet_layout.button, 6)
    main_layout.set(create_restart_button(board, style=ButtonStyle(**reds)), 7)

    brightness_widget = BrightnessWidget(board, style=ButtonStyle(**yellows))
    main_layout.set(brightness_widget.brightness_up_button, 0, 2)
    main_layout.set(brightness_widget.brightness_display_button, 1, 2)
    main_layout.set(brightness_widget.brightness_down_button, 2, 2)

    volume_widget = VolumeWidget(board, style=ButtonStyle(**oranges))
    main_layout.set(volume_widget.decrease_volume_button, 0, 3)
    main_layout.set(volume_widget.display_volume_button, 1, 3)
    main_layout.set(volume_widget.increase_volume_button, 2, 3)

    try:
        board.apply(main_layout)
        print("board started")
        while not board.shutdown:
            time.sleep(1.2)
    except Exception as e:
        print(e)
        raise
    finally:
        print("catching closing.")
        try:
            for button in board.buttons.values():
                button.reset(background_color=black)
            print("successfully reset button backgrounds")
        except:
            print("failed to reset button backgrounds")
            pass
        board.close()


def ignore_errors(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            pass
    return wrapped



if __name__ == '__main__':
    run_main()
    # sess = requests.Session()
    # resp: requests.Response = sess.get('https://camelcamelcamel.com/product/B07RL8H55Z?active=watch')
    # bs = BeautifulSoup(resp.content, 'html.parser')
    # script_str: str = [c for c in bs.find_all('script')[0].children][0]
    # string_re = re.compile(r"'([^']+)'")
    # strings = string_re.findall(script_str)
    # base64_strings = list(filter(None, [ignore_errors(base64.decodebytes)(string.encode()) for string in strings]))
    # import ipdb; ipdb.set_trace()
    # print()
