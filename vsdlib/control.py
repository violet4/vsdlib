from typing import List, Union, Callable
import logging

from pynput.keyboard import Controller, Key


logger = logging.getLogger(__file__)


# Create a Controller
controller = Controller()


def parse_keys(shortcut: str) -> Union[str, List[Union[Key, str]]]:
    """
    Parse a keyboard shortcut string into a list of keys.
    """
    if len(shortcut)==1:
        return [shortcut]
    elif '+' in shortcut or ',' in shortcut:
        parsed_keys = []
        for key in shortcut.split('+'):
            if hasattr(Key, key):
                parsed_keys.append(getattr(Key, key))
            else:
                parsed_keys.append(key)
        if parsed_keys:
            return parsed_keys
        return shortcut
    else:
        return shortcut


def create_execute_shortcut_function(command_string: str) -> Callable:
    """
    command_string examples:
        alt+k,alt-r
        alt+k
        j
        ctrl+c
    """
    parsed_keys = parse_keys(command_string)
    logger.debug("parsed keys from '%s': '%s'", command_string, parsed_keys)

    def execute_shortcut(pressed:bool) -> None:
        if not pressed:
            return
        if isinstance(parsed_keys, str):
            logger.debug("typing: %s", parsed_keys)
            controller.type(parsed_keys)
        else:
            # Press keys
            for key in parsed_keys:
                logger.debug("pressing (and not releasing): %s", key)
                controller.press(key)
            # Release keys in reverse order
            for key in reversed(parsed_keys):
                logger.debug("releasing key: %s", key)
                controller.release(key)

    return execute_shortcut


# Create an execute function for the shortcut "ctrl+w"
# close_window_fn = create_execute_shortcut_function('ctrl+w')

# # Execute the shortcut
# close_window_fn(controller)
