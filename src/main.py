from infi.systray import SysTrayIcon
from notifypy import Notify
from utils import Metadata, WindowsMediaInfo
from threading import Thread
import webbrowser as wbr
import socket
import os, sys
import shutil
import asyncio
import json
import copy
import eel


__version__ = "0.2.1"
SETTINGS = {}

#####
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def exe_path(relative_path):
    return os.path.join(os.getcwd(), relative_path)
#####


notification = Notify(
    default_notification_title=f"Melody Monitor {__version__}",
    default_application_name="Melody Monitor",
    default_notification_icon=resource_path(os.path.join("data", "music.ico"))
)


MediaInfo = Metadata()


async def update_media_info():
    global MediaInfo
    systemManager = WindowsMediaInfo()
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


#####

def load_settings():
    global SETTINGS
    with open(resource_path(os.path.join("data", "settings.json")), 'r', encoding='utf-8') as f:
        SETTINGS = json.loads(f.read())

    if os.path.exists(exe_path("settings.user.json")):
        with open(exe_path("settings.user.json"), 'r', encoding='utf-8') as f:
            try:
                user_settings = json.loads(f.read())
                SETTINGS.update(user_settings)
            except json.decoder.JSONDecodeError as e:
                notification.message = "Failed to load settings"
                notification.send()
                raise e

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
    if not os.path.exists(exe_path("settings.user.json")):
        with open(exe_path("settings.user.json"), 'w', encoding='utf-8') as f:
            f.write("{\n\t\n}")
    os.startfile(exe_path("settings.user.json"))

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

    notification.message = f"Running at {generate_url()}"
    notification.send()

    eel.start("index.html", host=SETTINGS.get('host'), port=SETTINGS.get('port'), mode=None, close_callback=lambda a, b: None)
