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
import time
import requests


__version__ = "1.4.0"
SETTINGS = None
MODS = []
MODS_SETTINGS = {}
FilteredApps = {
    "mode": "exclude",
    "apps": []
}

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
        systemManager.last_update = int(time.time())
        answer = copy.copy(localMediaInfo)
        if answer.thumbnail:
            answer.thumbnail = await answer.thumbnail.get()
        eel.update_media_info(vars(answer))
    else:
        if MediaInfo.status == "PLAYING":
            diff = int(time.time()) - getattr(systemManager, "last_update", 0)
            if diff > 0 and MediaInfo.current + diff < MediaInfo.total:
                answer = copy.copy(localMediaInfo)
                answer.current = MediaInfo.current + diff
                if answer.thumbnail:
                    answer.thumbnail = await answer.thumbnail.get()
                eel.update_media_info(vars(answer))


@eel.expose
def get_media_info():
    answer = copy.copy(MediaInfo)
    if MediaInfo.status == "PLAYING":
        diff = int(time.time()) - getattr(systemManager, "last_update", 0)
        if diff > 0 and MediaInfo.current + diff < MediaInfo.total:
            answer.current = MediaInfo.current + diff

    if answer.thumbnail:
        loop = asyncio.get_event_loop()
        answer.thumbnail = loop.run_until_complete(answer.thumbnail.get())
    eel.update_media_info(vars(answer))

@eel.expose
def get_active_sessions():
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(systemManager.get_active_sessions())
    return res

@eel.expose
def get_my_filters():
    return FilteredApps

@eel.expose
def update_filters(mode, apps):
    global FilteredApps
    FilteredApps = {
        "mode": mode,
        "apps": apps
    }
    systemManager.set_filters(FilteredApps["apps"], mode=FilteredApps["mode"])
    with open(exe_path("filters.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(FilteredApps, ensure_ascii=False))

async def addEventListeners():
    while True:
        await update_media_info()
        await asyncio.sleep(SETTINGS.get('interval'))

def startBackgroundLoop():
    asyncio.run(addEventListeners())


@eel.expose
def check_updates():
    try:
        r = requests.get('https://api.github.com/repos/SuperZombi/melody-monitor/releases/latest')
        if r.ok:
            remote_version = Version(r.json()['tag_name'])
            current_version = Version(__version__)
            if remote_version > current_version:
                return {
                    "current": str(current_version),
                    "new": str(remote_version)
                }
    except: None


@eel.expose
def get_mods_files():
    mods_folder = resource_path(os.path.join("web", "mods"))
    if os.path.exists(mods_folder):
        files = []
        for root, _, filenames in os.walk(mods_folder):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(root,filename), mods_folder))
        return files
    return []

@eel.expose
def get_mods_settings():
    attrs = {}
    vars = {}
    for key,val in MODS_SETTINGS.items():
        if val["enable"]:
            attrs = {**attrs, **val.get("settings", dict())}
            vars = {**vars, **val.get("vars", dict())}
    return {"attrs": attrs, "vars": vars}


@eel.expose
def get_user_settings():
    attrs = {}
    vars = {}
    for seti in SETTINGS.metadata:
        if seti["name"] in ["host", "port", "interval"]:
            continue
        if seti["namespace"] == "attr":
            attrs[seti["name"]] = seti["value"]
        elif seti["namespace"] == "var":
            vars[seti["name"]] = seti["value"]
    return {"attrs": attrs, "vars": vars}


@eel.expose
def get_settings():
    return SETTINGS.metadata
@eel.expose
def get_mods():
    return [mod.metadata for mod in MODS]


#####


def parse_config(data):
    settings = []
    for i in data:
        settings.append(Setting(**i))
    return settings


def load_settings():
    global SETTINGS, FilteredApps
    with open(resource_path(os.path.join("data", "settings.config.json")), 'r', encoding='utf-8') as f:
        template = parse_config(json.loads(f.read()))
        SETTINGS = SettingsManager(template)

    if os.path.exists(exe_path("settings.user.json")):
        with open(exe_path("settings.user.json"), 'r', encoding='utf-8') as f:
            user_settings = json.loads(f.read())
            SETTINGS.load_settings(user_settings)

    if os.path.exists(exe_path("filters.json")):
        with open(exe_path("filters.json"), 'r', encoding='utf-8') as f:
            FilteredApps = json.loads(f.read())
            systemManager.set_filters(FilteredApps["apps"], mode=FilteredApps["mode"])

def load_mods_settings():
    global MODS_SETTINGS
    if os.path.exists(exe_path("mods.settings.json")):
        with open(exe_path("mods.settings.json"), 'r', encoding='utf-8') as f:
            MODS_SETTINGS = json.loads(f.read())


@eel.expose
def update_setting(name, value):
    SETTINGS.set(name, value)

@eel.expose
def update_mod_setting(mod_id, enable, attrs, vars):
    global MODS_SETTINGS
    MODS_SETTINGS[mod_id]["enable"] = enable
    MODS_SETTINGS[mod_id]["settings"] = attrs
    MODS_SETTINGS[mod_id]["vars"] = vars

@eel.expose
def save_settings():
    with open(exe_path("settings.user.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(SETTINGS.json(True), indent=4))

@eel.expose
def save_mods_settings():
    with open(exe_path("mods.settings.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(MODS_SETTINGS, indent=4))

@eel.expose
def refresh(_=None):
    load_settings()
    load_mods()
    eel.update_url(generate_url())


def load_mods():
    global MODS_SETTINGS, MODS
    MODS = []
    MODS_SETTINGS = {}
    load_mods_settings()

    mods_folder = resource_path(os.path.join("web", "mods"))
    if os.path.exists(mods_folder):
        shutil.rmtree(mods_folder)
    os.makedirs(mods_folder)

    if os.path.exists(exe_path("mods")):
        for item in os.listdir(exe_path("mods")):
            item_path = os.path.join(exe_path("mods"), item)
            loader = ModLoader(item_path)
            mod = Mod(**loader.meta)

            if mod.id in MODS_SETTINGS:
                mod.update_settings(MODS_SETTINGS.get(mod.id))
            else:
                MODS_SETTINGS[mod.id] = mod.get_settings()
            MODS.append(mod)

            if MODS_SETTINGS[mod.id]["enable"]:
                loader.copy_files(os.path.join(mods_folder, mod.id))


@eel.expose
def mods_store():
    try:
        r = requests.get('https://raw.githubusercontent.com/SuperZombi/melody-monitor/refs/heads/main/mods/all.json')
        if r.ok:
            mods_info = json.loads(r.content.decode())
            return mods_info
    except: pass
    return []

@eel.expose
def install_mod(mod_id):
    mods_folder = exe_path("mods")
    if not os.path.exists(mods_folder): os.makedirs(mods_folder)
    target_file = os.path.join(mods_folder, f"{mod_id}.zip")
    if os.path.exists(target_file): return False
    url = f"https://github.com/SuperZombi/melody-monitor/raw/refs/heads/main/mods/{mod_id}/{mod_id}.zip"
    try:
        r = requests.get(url)
        if r.ok:
            with open(target_file, 'wb') as f:
                f.write(r.content)
            return True
    except: pass

@eel.expose
def remove_mod(mod_id):
    global MODS_SETTINGS
    def remove_settings():
        if mod_id in MODS_SETTINGS.keys():
            del MODS_SETTINGS[mod_id]
            save_mods_settings()
    target_file = os.path.join(exe_path("mods"), f"{mod_id}.zip")
    if os.path.exists(target_file):
        os.remove(target_file)
        remove_settings()
        return True
    target_folder = os.path.join(exe_path("mods"), mod_id)
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)
        remove_settings()
        return True

@eel.expose
def create_new_mod(data):
    mod_folder = os.path.join(exe_path("mods"), data.get("id"))
    if os.path.exists(mod_folder): return False
    
    os.makedirs(mod_folder)
    css_file = os.path.join(mod_folder, f"{data.get('id')}.css")
    shutil.copyfile(resource_path(os.path.join("data", "mod_template.css")), css_file)

    with open(os.path.join(mod_folder, "meta.json"), 'w', encoding="utf-8") as f:
        f.write(json.dumps({
            "id": data.get("id"),
            "name": data.get("name"),
            "author": data.get("author", ""),
            "description": data.get("description", ""),
            "icon": "",
            "files": [f"{data.get('id')}.css"]
        }, ensure_ascii=False, indent=4))

    os.startfile(mod_folder)
    return True


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
    if not os.path.exists(exe_path("mods")):
        os.mkdir(exe_path("mods"))
    wbr.open(generate_url() + "/settings.html")

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
        ("Open in Browser", resource_path(os.path.join("data", "browser.ico")), open_browser),
        ("Settings", resource_path(os.path.join("data", "settings.ico")), open_settings),
        ('Refresh', resource_path(os.path.join("data", "refresh.ico")), refresh)
    )
    systray = SysTrayIcon(resource_path(os.path.join("data", "music.ico")), "Melody Monitor", menu_options, on_quit=lambda _: os._exit(0))
    systray.start()

    eel.start("index.html", host=SETTINGS.get('host'), port=SETTINGS.get('port'), mode=None, close_callback=lambda a, b: None)
