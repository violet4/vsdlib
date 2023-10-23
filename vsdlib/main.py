import time
import argparse
import tomllib
from typing import Optional, TypedDict, NotRequired
import asyncio
import os
import logging
import sys

from pydantic import BaseModel

from vsdlib.board import Board, BoardLayout
from vsdlib.buttons import Button, ButtonStyle
from vsdlib.control import create_execute_shortcut_function

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class VSDLibNamespace(argparse.Namespace):
    toml_path: Optional[str]
    positions: bool
    log_level: str = 'INFO'


def list_log_levels():
    levels = [
        (a,getattr(logging,a))
        for a in dir(logging)
        if a.upper()==a
        and isinstance(getattr(logging, a), int)
    ]
    return [l[0] for l in sorted(levels, key=lambda a:a[1])]


def parse_args() -> VSDLibNamespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('toml_path', nargs='?', help='the toml file to create buttons from')
    parser.add_argument('--positions', default=False, action='store_true', help='use the demo "positions" board')
    parser.add_argument('--log-level', default=VSDLibNamespace.log_level, help=f"log level. default: %(default)s; options: {list_log_levels()}")
    args = parser.parse_args(namespace=VSDLibNamespace())
    return args


class ButtonSchema(BaseModel):
    """
    Absolute minimum a button can have is text and/or image, and zero or more button_schema_classes
    """
    text: str
    color: Optional[str] = None
    img: Optional[str] = None
    button_schema_classes: Optional[str] = None


#TODO:make a version that can start and interact with a separate thread that's listening for incoming connection requests
class PythonScriptButtonSchema(ButtonSchema):
    script_path: str

class PressButtonSchema(ButtonSchema):
    key: Optional[str] = None
    delay: Optional[float] = None

class ToggleButtonSchema(ButtonSchema):
    toggle: bool = False
    toggle_true_img: Optional[str] = None
    toggle_false_img: Optional[str] = None

class TogglePressButtonSchema(*[PressButtonSchema, ToggleButtonSchema]):
    pass

schema_name_to_schema = {
    'PythonScriptButtonSchema': PythonScriptButtonSchema,
    'PressButtonSchema': PressButtonSchema,
    'ToggleButtonSchema': ToggleButtonSchema,
    'TogglePressButtonSchema': TogglePressButtonSchema,
}


# In [15]: with con.pressed('2'):
#     ...:     time.sleep(0.1)

class Kwargs(TypedDict):
    background_color: NotRequired[str]
    text_color: NotRequired[str]
    font_size: NotRequired[int | str]
    pressed_background_color: NotRequired[str]
    image_path: NotRequired[str]


def produce_positions_data(cols:int, rows:int) -> dict:
    from collections import defaultdict
    data = defaultdict(dict)
    for col in range(cols):
        for row in range(rows):
            data[f'c{col}'][f'r{row}'] = {
                'text': f'{col},{row}',
            }

    return data


def create_button_position_generator(width:int, height:int):
    for wid in range(width):
        row = f'r{wid}'
        for hei in range(height):
            col = f'c{hei}'
            yield f'{col}.{row}'
            yield f'{row}.{col}'


async def main_helper(board:Board, args:VSDLibNamespace):

    logger.debug(args)
    logger.debug(args.toml_path)
    layout = BoardLayout()
    if args.positions:
        data = produce_positions_data(BoardLayout.width, BoardLayout.height)

    elif args.toml_path:
        with open(args.toml_path, 'rb') as fr:
            # Read TOML and validate
            data = tomllib.load(fr)
    else:
        logger.fatal("toml_path or --positions required")
        exit(1)

    colors: dict = data.get('colors', {})
    valid = True
    logger.debug('BoardLayout.height %s', BoardLayout.height)
    for col_num in range(BoardLayout.width):
        ck = f'c{col_num}'
        col = data.get(ck, None)
        if col is None:
            continue

        for row_num in range(BoardLayout.height):
            rk = f'r{row_num}'
            button_dict = col.get(rk, None)
            if button_dict is None:
                continue

            button_data = ButtonSchema(**button_dict)
            # import pdb; pdb.set_trace()
            schema_names = list(filter(None, (button_data.button_schema_classes or '').split(',')))
            logger.info('schema_names: %s', schema_names)
            button_schema_classes = [
                schema_name_to_schema[name]
                for name in schema_names
            ]
            logger.info("button_schema_classes: %s", button_schema_classes)
            button_data.color = colors.get(button_data.color, button_data.color)
            print(f"button {rk}.{ck}: {button_data}")

            kwargs: Kwargs = {}
            # handle cases from most specific to least specific
            if button_data.img:
                if os.path.exists(button_data.img):
                    kwargs['image_path'] = button_data.img
                else:
                    logger.error("image_path was provided but doesn't exist: '%s'", button_data.img)
                    valid = False
            elif button_data.color:
                kwargs['background_color'] = button_data.color

            button_fn = None
            if button_schema_classes:
                class ValidatorClass(*button_schema_classes):
                    pass
                button_data_extra = ValidatorClass(**button_dict)
                if isinstance(button_data_extra, PressButtonSchema):
                    button_fn = create_execute_shortcut_function(button_data_extra.key, button_data_extra.delay) if button_data_extra.key else None

            button = Button(
                fn=button_fn, name=None, text=button_data.text,
                style=ButtonStyle(
                    **kwargs,
                    # background_color,
                    # text_color,
                    # pressed_background_color,
                    # image_path,
                ),
            )
            layout.set(button, col_num, row_num)

    if not valid:
        print("toml file validation failed; please fix errors")
        exit(1)

    layout.apply(board)
    while not board.shutdown:
        await asyncio.sleep(1.2)


def main():
    args = parse_args()
    log_level = getattr(logging, args.log_level)
    logger.setLevel(level=log_level)
    logging.basicConfig(level=log_level)

    if args.log_level.lower() == 'debug':
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(pathname)s:%(lineno)d:%(message)s')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    board = Board()
    BoardLayout.initialize(board)
    try:
        loop = asyncio.get_event_loop()
        init_ok = loop.run_until_complete(main_helper(board, args))
        if init_ok:
            loop.run_forever()
    finally:
        board.close()
