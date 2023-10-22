from typing import Union, List, Dict, Optional, Any

import subprocess
import logging
import stat
from contextlib import contextmanager
import tempfile
import os


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


options: Dict[str, Optional[Any]] = {
    'environment_file': None,
}


class Success:
    def __init__(self, value):
        self.value = bool(value)

    def __bool__(self):
        return self.value


def get_application_ids(class_name:str):
    return subprocess.Popen(['xdotool', 'search', '--class', class_name], stdout=subprocess.PIPE)

def activate_application(class_name:str) -> Success:
    # commit: fix: application activation: properly handle when no matching windows returns [''] (previously broke things)
    xdotool_ids = list(filter(None, get_application_ids(class_name).communicate()[0].decode().strip().split('\n')))
    if not xdotool_ids:
        return Success(False)

    #TODO:what's h appening here? why do we do this work multiple times? don't want to deal with it right this moment :p
    for xdotool_id in xdotool_ids:
        retcode = subprocess.call(
            ['xdotool', 'windowactivate', xdotool_id],
        )
        #TODO:?
        if retcode == 0:
            break

    xdotool_ids = get_application_ids(class_name)
    open_windows_process = subprocess.Popen(['bash', '-c', """
        while read window_id ; do xdotool windowactivate $window_id ; done
    """], stdin=xdotool_ids.stdout)
    open_windows_process.communicate()
    print(f"open_windows.returncode {open_windows_process.returncode}")
    return Success(open_windows_process.returncode==0)


@contextmanager
def mkstemp(*args, delete:bool=True, **kwargs):
    fd, exe_filepath = tempfile.mkstemp(*args, **kwargs)
    yield fd, exe_filepath
    if delete:
        os.remove(exe_filepath)


def construct_exe_file_contents(binary_path:str):
    env_setup = ''
    if options['environment_file'] is not None:
        # grab environment from the environment file our parent process created
        env_setup = 'source "{}"\n'.format(options['environment_file'])
    else:
        # fresh environment
        env_setup = "env -i HOME=$HOME DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY "
    exe_file_contents = f"{env_setup}{binary_path}"
    return exe_file_contents


def create_activate_application(app_name:Union[str, List[str]], binary_path:str):
    """
    never pass untrusted user input to binary_path
    """
    app_names = [app_name] if isinstance(app_name, str) else app_name

    def new_activate_application(pressed:bool):
        if not pressed:
            return
        for aname in app_names:
            #commit:ensure we're using `logging` module instead of printing everywhere
            logger.debug(f"trying to activate app name: {aname}")
            success = Success(False)
            try:
                success = activate_application(aname)
            except Exception as e:
                logger.error(f"Failed to activate {aname}: {e}")
            logger.debug(f"success: {success} {success.value} bool(success) {bool(success)}")
            if bool(success):
                logger.debug("success='%s'?.. returning..", success)
                return

        #TODO:secure method would ensure binary_path exists.. but also needs to check for spaces and - for user trying to splice in command-line arguments
        exe_file_contents = construct_exe_file_contents(binary_path)
        with mkstemp(suffix='vsdlib.sh', text=True, delete=False) as (fd, exe_filepath):
            with open(fd, 'w') as fw:
                print(exe_file_contents, file=fw)

            # make executable for this user
            st = os.stat(exe_filepath)
            os.chmod(exe_filepath, st.st_mode|stat.S_IXUSR)

            nohup_wrapper = f'nohup bash "{exe_filepath}" &'
            logger.debug(
                'attempting command: binary_path, nohup_wrapper, exe_file_contents: *****\n%s\n*****\n%s\n*****\n%s\n*****',
                binary_path, nohup_wrapper, exe_file_contents,
            )
            logger.debug("calling: %s", nohup_wrapper)
            subprocess.call(nohup_wrapper, shell=True)

    return new_activate_application


activate_terminal = create_activate_application('xfce4-terminal', '/usr/bin/xfce4-terminal')
activate_gimp = create_activate_application('gimp', '/usr/bin/gimp')
activate_thunderbird = create_activate_application('betterbird', '/home/violet/Downloads/betterbird/betterbird/betterbird')
activate_firefox = create_activate_application('firefox', '/usr/bin/firefox-bin')
activate_thunar = create_activate_application('thunar', '/usr/bin/thunar')
activate_joplin = create_activate_application('joplin', '/home/violet/Downloads/Joplin-2.13.2.AppImage')
activate_keepassxc = create_activate_application('keepassxc', '/usr/bin/keepassxc')
activate_discord = create_activate_application('discord', '/usr/bin/discord')
activate_pavucontrol = create_activate_application('pavucontrol', '/usr/bin/pavucontrol')
activate_minecraft = create_activate_application(['minecraft', 'ATLauncher'], '/usr/bin/ATLauncher')


def minimize_current_window():
    try:
        window_name = subprocess.check_output(['xdotool', 'getactivewindow', 'getwindowname']).strip().decode()
    except:
        print("ERROR: failed to get window name; therefore can't minimize")
        return
    # don't try to hide 'Desktop' otherwise we'll get really odd behavior
    print("WINDOW NAME FOR HIDING", window_name)
    if window_name == 'Desktop':
        return

    try:
        window_id = int(subprocess.check_output(['xdotool', 'getactivewindow']))
    except:
        return
    subprocess.call(['xdotool', 'windowminimize', str(window_id)])
