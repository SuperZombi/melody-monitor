import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlayStatus
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions
import json


class Thumbnail:
    def __init__(self): pass
    async def new(self, thumbnail):
        self.thumb = await thumbnail.open_read_async()
        return self

    async def get(self):
        buffer = Buffer(self.size)
        await thumb.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
        buffer_reader = DataReader.from_buffer(buffer)
        byte_buffer = bytearray(buffer_reader.read_buffer(buffer.length))
        return byte_buffer

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


async def addEventListeners():
    while True:
        await get_media_info()
        await asyncio.sleep(3)

    # event = asyncio.Event()
    # await event.wait()


if __name__ == '__main__':
    current_media_info = asyncio.run(addEventListeners())