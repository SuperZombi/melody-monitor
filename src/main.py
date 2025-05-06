from infi.systray import SysTrayIcon
from utils import *
from threading import Thread
import webbrowser as wbr
import socket
import platform
import os, sys
import shutil
import asyncio
import json
import copy
import eel


__version__ = "1.0.0"
SETTINGS = None

#####
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def exe_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)
#####


MediaInfo = Metadata()

platform = platform.system().lower()
if platform == "windows":
    systemManager = WindowsMediaInfo()
else:
    raise OSError(f"UnsupportedPlatform: {platform}")


async def update_media_info():
    global MediaInfo
    localMediaInfo = await systemManager.get_media_info()

    if not localMediaInfo == MediaInfo:
        MediaInfo = localMediaInfo
        answer = copy.copy(localMediaInfo)
        if answer.thumbnail:
            answer.thumbnail = await answer.thumbnail.get()
        eel.update_media_info(vars(answer))


@eel.expose
def get_media_info():
    answer = copy.copy(MediaInfo)
    if answer.thumbnail:
        loop = asyncio.get_event_loop()
        answer.thumbnail = loop.run_until_complete(answer.thumbnail.get())
    eel.update_media_info(vars(answer))


async def addEventListeners():
    while True:
        await update_media_info()
        await asyncio.sleep(SETTINGS.get('interval'))

def startBackgroundLoop():
    asyncio.run(addEventListeners())


@eel.expose
def get_mods_list():
    if os.path.exists(resource_path(os.path.join("web", "mods"))):
        return [f for f in os.listdir(resource_path(os.path.join("web", "mods")))]
    return []

@eel.expose
def get_user_settings():
    if os.path.exists(exe_path("settings.user.json")):
        with open(exe_path("settings.user.json"), 'r', encoding='utf-8') as f:
            s = json.loads(f.read())
            return dict(filter(
                lambda x: x[0] not in ["host", "port", "interval"],
                s.items()
            ))
    return {}


@eel.expose
def get_settings():
    return SETTINGS.metadata


#####


def parse_config(data):
    settings = []
    for i in data:
        settings.append(Setting(**i))
    return settings


def load_settings():
    global SETTINGS
    with open(resource_path(os.path.join("data", "settings.config.json")), 'r', encoding='utf-8') as f:
        template = parse_config(json.loads(f.read()))
        SETTINGS = SettingsManager(template)

    if os.path.exists(exe_path("settings.user.json")):
        with open(exe_path("settings.user.json"), 'r', encoding='utf-8') as f:
            user_settings = json.loads(f.read())
            SETTINGS.load_settings(user_settings)


@eel.expose
def update_setting(name, value):
    SETTINGS.set(name, value)

@eel.expose
def save_settings():
    with open(exe_path("settings.user.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(SETTINGS.json(True), indent=4))
    eel.update_url(generate_url())


def load_mods():
    if os.path.exists(resource_path(os.path.join("web", "mods"))):
        shutil.rmtree(resource_path(os.path.join("web", "mods")))
    if os.path.exists(exe_path("mods")):
        shutil.copytree(exe_path("mods"), resource_path(os.path.join("web", "mods")))


######
def generate_url():
    host = SETTINGS.get('host')
    if host == "0.0.0.0":
        host = socket.gethostbyname(socket.gethostname())
    return f"http://{host}:{SETTINGS.get('port')}"


#######
def open_browser(_):
    wbr.open(generate_url())

def open_settings(_):
    wbr.open(generate_url() + "/settings.html")

def open_mods_folder(_):
    if not os.path.exists(exe_path("mods")):
        os.mkdir(exe_path("mods"))
    os.startfile(exe_path("mods"))

def open_mods_url(_):
    wbr.open("https://github.com/SuperZombi/melody-monitor/tree/main/mods")

def refresh_settings_mods(_):
    load_settings()
    load_mods()
    eel.update_url(generate_url())


if __name__ == '__main__':
    load_settings()
    load_mods()
    eel.init(resource_path("web"))

    Thread(target=startBackgroundLoop, daemon=True).start()

    menu_options = (
        ("Open in Browser", None, open_browser),
        ("Settings", None, (
            ('Open Settings', None, open_settings),
            ('Mods Folder', None, open_mods_folder),
            ('Download Mods', None, open_mods_url),
            ('Refresh', None, refresh_settings_mods)
        ))
    )
    systray = SysTrayIcon(resource_path(os.path.join("data", "music.ico")), "Melody Monitor", menu_options, on_quit=lambda _: os._exit(0))
    systray.start()

    eel.start("index.html", host=SETTINGS.get('host'), port=SETTINGS.get('port'), mode=None, close_callback=lambda a, b: None)
