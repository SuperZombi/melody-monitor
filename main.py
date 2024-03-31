from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlayStatus
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from infi.systray import SysTrayIcon
from threading import Thread
import webbrowser as wbr
import socket
import os, sys
import shutil
import asyncio
import json
import base64
import copy
import eel


__version__ = "0.2.0"
SETTINGS = {}


def equals(set1, set2):
    def serialize(cls):
        return cls.__repr__()
    return json.dumps(set1, default=serialize) == json.dumps(set2, default=serialize)


class Thumbnail:
    def __init__(self): pass
    async def new(self, thumbnail):
        self.thumb = await thumbnail.open_read_async()
        self.result = None
        return self

    async def get(self):
        if self.result: return self.result
        buffer = Buffer(self.thumb.size)
        await self.thumb.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
        buffer_reader = DataReader.from_buffer(buffer)
        byte_buffer = bytearray(buffer_reader.read_buffer(buffer.length))
        img_base64 = base64.b64encode(byte_buffer).decode('utf-8')
        self.result = f"data:image/jpeg;base64,{img_base64}"
        return self.result

    def __repr__(self):
        return str(self.thumb.size)

MediaInfo = {}

async def update_media_info():
    global MediaInfo
    localMediaInfo = {}
    manager = await MediaManager.request_async()

    active_sessions = list(
        filter(lambda session: session.get_playback_info().playback_status == PlayStatus.PLAYING,
        manager.get_sessions())
    )
    if len(active_sessions) > 0:
        current_session = active_sessions[0]
    else:
        current_session = manager.get_current_session()
    
    if current_session:
        playback_info = current_session.get_playback_info()
        play_status = playback_info.playback_status
        if play_status in [PlayStatus.PLAYING, PlayStatus.PAUSED]:
            localMediaInfo["status"] = play_status.name

            timeline_properties = current_session.get_timeline_properties()
            localMediaInfo["current"] = int(timeline_properties.position.total_seconds())
            localMediaInfo["total"] = int(timeline_properties.end_time.total_seconds())
            
            info = await current_session.try_get_media_properties_async()
            localMediaInfo["artist"] = info.artist
            localMediaInfo["title"] = info.title

            thumbnail = info.thumbnail
            if thumbnail:
                localMediaInfo["thumbnail"] = await Thumbnail().new(thumbnail)

    if not equals(localMediaInfo, MediaInfo):
        MediaInfo = localMediaInfo
        print(MediaInfo)

        answer = copy.copy(localMediaInfo)
        if answer.get("thumbnail"):
            answer["thumbnail"] = await answer["thumbnail"].get()
        eel.update_media_info(answer)


@eel.expose
def get_media_info():
    answer = copy.copy(MediaInfo)
    if answer.get("thumbnail"):
        loop = asyncio.get_event_loop()
        answer["thumbnail"] = loop.run_until_complete(answer["thumbnail"].get())
    eel.update_media_info(answer)


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
            return json.loads(f.read())
    return {}


#####
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def exe_path(relative_path):
    return os.path.join(os.getcwd(), relative_path)
#####

def load_settings():
    global SETTINGS
    with open(resource_path(os.path.join("data", "settings.json")), 'r', encoding='utf-8') as f:
        SETTINGS = json.loads(f.read())

    if os.path.exists(exe_path("settings.user.json")):
        with open(exe_path("settings.user.json"), 'r', encoding='utf-8') as f:
            user_settings = json.loads(f.read())
            SETTINGS.update(user_settings)

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

    eel.start("index.html", host=SETTINGS.get('host'), port=SETTINGS.get('port'), mode=None, close_callback=lambda a, b: None)
