from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlayStatus
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from threading import Thread
import os, sys
import asyncio
import json
import base64
import copy
import eel


class Thumbnail:
    def __init__(self): pass
    async def new(self, thumbnail):
        self.thumb = await thumbnail.open_read_async()
        return self

    async def get(self):
        buffer = Buffer(self.thumb.size)
        await self.thumb.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
        buffer_reader = DataReader.from_buffer(buffer)
        byte_buffer = bytearray(buffer_reader.read_buffer(buffer.length))
        img_base64 = base64.b64encode(byte_buffer).decode('utf-8')
        img_data_url = f"data:image/jpeg;base64,{img_base64}"
        return img_data_url

    def __repr__(self):
        return str(self.thumb.size)


def equals(set1, set2):
    def serialize(cls):
        return cls.__repr__()
    return json.dumps(set1, default=serialize) == json.dumps(set2, default=serialize)



MediaInfo = {}

async def get_media_info():
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


async def addEventListeners():
    while True:
        await get_media_info()
        await asyncio.sleep(3)

def startBackgroundLoop():
    asyncio.run(addEventListeners())


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    eel.init(resource_path("web"))

    Thread(target=startBackgroundLoop, daemon=True).start()

    eel.start("index.html", mode="default")
