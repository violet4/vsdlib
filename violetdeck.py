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
import asyncio
import subprocess
import argparse
from typing import Optional
import logging

from vsdlib.widgets import (
    VolumeWidget, BrightnessWidget, MediaControlWidget, DiscordWidget,
    ClockWidget
)
from vsdlib.board import Board, BoardLayout
from vsdlib.buttons import Button, ButtonStyle
from vsdlib.colors import reds, oranges, yellows, greens, blues, purples, black, pinks, indigos, violets
from vsdlib.layouts import (
    TimerLayout, CalcLayout, PositionLayout, AlphabetLayout, BluetoothLayout, NumpadLayout, NotesLayout,
    RecurringTasksLayout, MedTrackerLayout, EmojiPadLayout, aTimeLoggerLayout, VSCodeLayout
)
from vsdlib.images import get_asset_path

from vsdlib.contrib.quicksilver import (
    activate_terminal, activate_thunderbird, activate_firefox,
    activate_thunar,
    minimize_current_window, activate_joplin,
    activate_discord, activate_gimp, activate_minecraft
)
from vsdlib.contrib import quicksilver


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


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


def do_if_pressed(fn):
    def wrapped(pressed:bool):
        print("pressed:", pressed)
        if not pressed:
            return
        return fn()
    return wrapped


def setup_audio_compression():
    subprocess.call(
        """
        # ensure that if we already had a sink that we remove it. ignore errors.
        pactl unload-module module-ladspa-sink 2>/dev/null
        sleep 1

        # figure out which output device we're currently using
        audio_ID=$(pactl list sinks short | awk '$7 == "RUNNING" {print $2}')

        # create a new virtual compressed audio device
        pactl load-module module-ladspa-sink sink_name=compressed master=$audio_ID plugin=fast_lookahead_limiter_1913 label=fastLookaheadLimiter control=5,-15,0.3
        # grab the ID of the new sink we just created
        compressed_sink_index=$(pactl list sinks short | awk '/compressed/ {print $1}')

        # move all existing audio streams to the new sink. this will
        # throw an error "Failure: Invalid argument" because you can't move
        # the compression output to itself.
        pactl list sink-inputs short | awk '{print $1}' | xargs -I {} pactl move-sink-input {} $compressed_sink_index

        # exit cleanly
        exit 0
        """,
        shell=True,
    )


async def run_main():
# def run_main():
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
    # timer = TimerLayout(board, main_layout)
    bluetooth = BluetoothLayout(board, main_layout)
    numpad = NumpadLayout(board, main_layout)
    # emoji_pad = EmojiPadLayout(board, main_layout)
    # atimelogger = aTimeLoggerLayout(board, main_layout)
    # notes = NotesLayout(board, main_layout)
    recur_tasks = RecurringTasksLayout(board, main_layout)
    # med_tracker = MedTrackerLayout(board, main_layout)
    vscode = VSCodeLayout(board, main_layout)

    brightness_widget = BrightnessWidget(board, style=ButtonStyle(**yellows))
    volume_widget = VolumeWidget(board, style=ButtonStyle(**oranges))
    media_control_widget = MediaControlWidget()
    discord_widget = DiscordWidget(board, style=ButtonStyle(**pinks))
    clock_widget = ClockWidget(board)

    discord_image_path = get_asset_path('discord-logo.jpg')
    joplin_image_path = get_asset_path('joplin.jpg')
    firefox_image_path = get_asset_path('firefox.jpg')
    thunar_image_path = get_asset_path('thunar.jpg')
    keepassxc_image_path = get_asset_path('KeePassXC.jpg')
    terminal_image_path = get_asset_path('Terminal.jpg')
    # betterbird_image_path = get_asset_path('betterbird.jpg')
    betterbird_image_path = get_asset_path('mail.jpg')

    discord_button = Button(activate_discord, text="Discord", style=ButtonStyle(**pinks, image_path=discord_image_path))
    joplin_button = Button(activate_joplin, text="Joplin", style=ButtonStyle(**pinks, image_path=joplin_image_path))
    keepass_button = Button(lambda: subprocess.call(['/usr/bin/keepassxc']), text="Kee\nPass\nXC", style=ButtonStyle(**pinks, image_path=keepassxc_image_path))
    terminal_button = Button(activate_terminal, text="Terminal", style=ButtonStyle(**pinks, image_path=terminal_image_path))
    thunderbird_button = Button(activate_thunderbird, text="BB", style=ButtonStyle(**pinks, image_path=betterbird_image_path))
    firefox_button = Button(activate_firefox, text="Firefox", style=ButtonStyle(**pinks, image_path=firefox_image_path))
    thunar_button = Button(activate_thunar, text="Thunar", style=ButtonStyle(**pinks, image_path=thunar_image_path))
    minimize_button = Button(do_if_pressed(minimize_current_window), text="Min", style=ButtonStyle(image_path=get_asset_path('minimize.jpg')))
    audio_compress_button = Button(do_if_pressed(setup_audio_compression), text="Audio\nCompress", style=ButtonStyle(image_path=get_asset_path('audio_compress.jpg')))
    gimp_button = Button(activate_gimp, style=ButtonStyle(image_path=get_asset_path('gimp.jpg')))
    minecraft_button = Button(activate_minecraft, style=ButtonStyle(image_path=get_asset_path('minecraft.jpg')))

    # main page top bar - x,0
    main_layout.set(position_layout.button, 0, 0)
    main_layout.set(calc.button,  3, 0)
    main_layout.set(bluetooth.button, 2, 0)
    main_layout.set(minimize_button,      1, 0)

    # main_layout.set(TODO.button, 4)
    main_layout.set(create_restart_button(board, style=ButtonStyle(**reds, image_path=get_asset_path('restart.jpg'))), 7, 0)
    main_layout.set(board.debug_button, 6, 0)

    # second row - x,1

    pp = media_control_widget.playpause
    back = media_control_widget.prevtrack
    # fullscreen = media_control_widget.full_screen
    forward = media_control_widget.nexttrack

    brightness = brightness_widget.brightness_display_button
    dim = brightness_widget.brightness_down_button
    brighten = brightness_widget.brightness_up_button

    volume = volume_widget.display_volume_button
    toggle_discord_mute = discord_widget.toggle_mute_button
    louder = volume_widget.increase_volume_button
    quieter = volume_widget.decrease_volume_button
    alphabet = alphabet_layout.button

    main_layout.set(toggle_discord_mute,         7, 1)
    # main_layout.set(emoji_pad.button,    7, 2)
    main_layout.set(clock_widget.clock_button,   7, 2)
    main_layout.set(alphabet,            7, 3)

    # main_layout.set(atimelogger.button,  6, 2)

    main_layout.set(vscode.button,       3, 1)
    main_layout.set(terminal_button,     3, 2)
    main_layout.set(firefox_button,      3, 3)
    # main_layout.set(timer.button,        5, 3)

    main_layout.set(recur_tasks.button, 4, 0)
    main_layout.set(minecraft_button,     4, 1)
    main_layout.set(gimp_button,     4, 2)
    main_layout.set(keepass_button,     4, 3)
    main_layout.set(audio_compress_button,        5, 0)
    main_layout.set(thunar_button,     5, 2)

    # main_layout.set(fullscreen,          3, 2)

    main_layout.set(joplin_button,       2, 1)
    main_layout.set(thunderbird_button,  2, 2)
    main_layout.set(discord_button,      2, 3)
    # main_layout.set(med_tracker.button,  3, 3)

    #TODO
    # 2,2 volume up
    # 1,1 back
    # 1,2 pp
    # 1,3 forard
    # 0,2 volume down

    layout = [
        ((dim,     6, 1), (brightness, 6, 2), (brighten, 6, 3)),
        ((back,    1, 1), (pp,         1, 2), (forward,  1, 3)),
        ((quieter, 0, 1), (volume,     0, 2), (louder,   0, 3)),
    ]
    for row in layout:
        for args in row:
            main_layout.set(*args)

    try:
        board.apply(main_layout)
        print("board started")
        while not board.shutdown:
            await asyncio.sleep(1.2)
    except Exception as e:
        print(e)
        raise
    finally:
        print("shutting down board..")
        try:
            for button in board.buttons.values():
                button.reset(background_color=black)
            print("successfully reset button backgrounds")
        except:
            print("failed to reset button backgrounds")
            pass
        board.close()
    return True


def ignore_errors(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            pass
    return wrapped


class Namespace(argparse.Namespace):
    environment_file: Optional[str]


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--environment-file', default=None)
    pargs = parser.parse_args(namespace=Namespace())
    return pargs


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    pargs = parse_arguments()
    if pargs.environment_file is not None:
        logger.debug("received environment file '%s'", pargs.environment_file)
        quicksilver.options['environment_file'] = pargs.environment_file
    else:
        logger.debug('received no env file')

    # sess = requests.Session()
    # resp: requests.Response = sess.get('https://camelcamelcamel.com/product/B07RL8H55Z?active=watch')
    # bs = BeautifulSoup(resp.content, 'html.parser')
    # script_str: str = [c for c in bs.find_all('script')[0].children][0]
    # string_re = re.compile(r"'([^']+)'")
    # strings = string_re.findall(script_str)
    # base64_strings = list(filter(None, [ignore_errors(base64.decodebytes)(string.encode()) for string in strings]))
    # import ipdb; ipdb.set_trace()
    # print()

    # run_main()

    loop = asyncio.get_event_loop()
    init_ok = loop.run_until_complete(run_main())
    if init_ok:
        loop.run_forever()
