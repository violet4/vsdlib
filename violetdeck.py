#!/usr/bin/env python3
"""
Button manages creating/producing pictures while Board manages index locations and setting the picture
"""
import os
import time


from vsdlib.widgets import VolumeWidget, BrightnessWidget, CalculatorWidget
from vsdlib.board import Board, BoardLayout
from vsdlib.buttons import Button, ButtonStyle
from vsdlib.colors import reds, oranges, yellows, greens, blues, purples, black, pinks


def color_generator():
    while True:
        for color in (reds, oranges, yellows, greens, blues, purples):
            yield color


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
    board = Board()

    BoardLayout.initialize(board.width)

    main_layout = BoardLayout(board.key_count)
    # main_layout_button: Button = main_layout.create_return_button(board, "< Home")

    alphabet_layout, alphabet_page_button = main_layout.sublayout(board, "Alphabet", style=ButtonStyle(**pinks))
    for i, (letter, colors) in enumerate(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', color_generator()), 1):
        # alphabet_board.set_button(i+1, text=letter, **colors)
        alphabet_layout.set(Button(text=letter, style=ButtonStyle(**colors)), i)

    calc_layout, calc_button = main_layout.sublayout(board, "Calc", style=ButtonStyle(**blues))
    calcwid = CalculatorWidget(board, style=ButtonStyle(**greens))

    i = 1
    for y in range(2, 0-1, -1):
        for x in range(board.width-3, board.width):
            calc_layout.set(getattr(calcwid, f'b{i}'), x, y)
            i += 1
            if i == 10:
                i = 0
    calc_layout.set(calcwid.b0, 6, 3)

    calc_layout.set(calcwid.spool_display_widget, 4,0)
    calc_layout.set(calcwid.bvalue, 4,1)

    calc_layout.set(calcwid.bplus, 0,1)
    calc_layout.set(calcwid.bminus, 0,2)
    calc_layout.set(calcwid.bequals, 7,3)
    calc_layout.set(calcwid.bmult, 1,1)
    calc_layout.set(calcwid.bdiv, 1,2)
    calc_layout.set(calcwid.bbackspace, 4,3)
    calc_layout.set(calcwid.bdecimal, 5,3)

    position_layout, positions_button = main_layout.sublayout(board, "Positions", style=ButtonStyle(**greens))
    for x in range(board.width):
        for y in range(board.height):
            if x+y == 0:
                continue
            if position_layout.calc_index(x,y) == board.key_count-1:
                text = f"{x}, {y}\nwidth={board.width}\nheight={board.height}"
            else:
                text = f"{x},{y}"
            position_layout.set(Button(text=text), x,y)

    # main page top bar
    main_layout.set(positions_button, 0)
    main_layout.set(calc_button, 1)
    # ..
    main_layout.set(alphabet_page_button, 6)
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
