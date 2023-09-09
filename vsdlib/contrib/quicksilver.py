from typing import Union, List


import subprocess


class Success:
    def __init__(self, value):
        self.value = bool(value)

    def __bool__(self):
        return self.value


def get_application_ids(class_name):
    return subprocess.Popen(['xdotool', 'search', '--class', class_name], stdout=subprocess.PIPE)

def activate_application(class_name) -> Success:
    xdotool_ids = get_application_ids(class_name).communicate()[0].decode().strip()
    if not xdotool_ids:
        return Success(False)

    xdotool_ids = get_application_ids(class_name)
    open_windows = subprocess.Popen(['bash', '-c', """
        while read window_id ; do xdotool windowactivate $window_id ; done
    """], stdin=xdotool_ids.stdout)
    open_windows.communicate()
    return Success(open_windows.returncode==0)


def activate_terminal():
    return activate_application('xfce4-terminal')

def create_activate_application(app_name:Union[str, List[str]], binary_path:str):
    app_names = [app_name] if isinstance(app_name, str) else app_name

    def new_activate_application():
        for aname in app_names:
            success = activate_application(aname)
            if success:
                return
        subprocess.call(f"""
            pwd; nohup bash -c {binary_path} &
        """, shell=True)
    return new_activate_application


activate_gimp = create_activate_application('gimp', '/usr/bin/gimp')
activate_thunderbird = create_activate_application('betterbird', '/home/violet/Downloads/betterbird/betterbird/betterbird')
activate_firefox = create_activate_application('firefox', '/usr/bin/firefox-bin')
activate_thunar = create_activate_application('thunar', '/usr/bin/thunar')
activate_joplin = create_activate_application('joplin', '/home/violet/Downloads/Joplin-2.11.11.AppImage')
activate_discord = create_activate_application('discord', '/usr/bin/discord')
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
