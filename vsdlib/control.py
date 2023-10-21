from pynput.keyboard import Controller, Key
from typing import List, Union, Callable

# Create a Controller
controller = Controller()


def parse_keys(shortcut: str) -> List[Union[Key, str]]:
    """
    Parse a keyboard shortcut string into a list of keys.
    """
    parsed_keys = []
    for key in shortcut.split('+'):
        if hasattr(Key, key):
            parsed_keys.append(getattr(Key, key))
        else:
            parsed_keys.append(key)
    return parsed_keys


def create_execute_shortcut_function(command_string: str) -> Callable:
    """
    command_string examples:
        alt+k,alt-r
        alt+k
        j
        ctrl+c
    """
    parsed_keys = parse_keys(command_string)

    def execute_shortcut(pressed:bool) -> None:
        if not pressed:
            return
        # Press keys
        for key in parsed_keys:
            controller.press(key)
        # Release keys in reverse order
        for key in reversed(parsed_keys):
            controller.release(key)

    return execute_shortcut


# Create an execute function for the shortcut "ctrl+w"
close_window_fn = create_execute_shortcut_function('ctrl+w')

# # Execute the shortcut
# close_window_fn(controller)
