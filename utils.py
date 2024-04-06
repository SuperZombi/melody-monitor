from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlayStatus
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from dataclasses import dataclass
from abc import ABC, abstractmethod
import base64


class Thumbnail:
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, thumbnail):
        self.thumb = await thumbnail.open_read_async()
        self.size = self.thumb.size
        self.result = None

    async def get(self) -> str:
        if self.result: return self.result
        buffer = Buffer(self.size)
        await self.thumb.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
        buffer_reader = DataReader.from_buffer(buffer)
        byte_buffer = bytearray(buffer_reader.read_buffer(buffer.length))
        img_base64 = base64.b64encode(byte_buffer).decode('utf-8')
        self.result = f"data:image/jpeg;base64,{img_base64}"
        return self.result

    def __eq__(self, other):
        return self.size == other.size


@dataclass
class Metadata():
    artist: str = ""
    title: str = ""
    current: int = 0
    total: int = 0
    status: str = None
    thumbnail: Thumbnail = None

    def __eq__(self, other):
        return (
            self.artist == other.artist and
            self.title == other.title and
            self.current == other.current and
            self.total == other.total and
            self.status == other.status and
            self.thumbnail == other.thumbnail
        )



class MediaInfoInterface(ABC):
    def __init__(self): pass

    @abstractmethod
    async def get_media_info(self) -> Metadata: pass



class WindowsMediaInfo():
    def __init__(self): pass

    async def get_session(self):
        manager = await MediaManager.request_async()

        active_sessions = list(
            filter(lambda session: session.get_playback_info().playback_status == PlayStatus.PLAYING,
            manager.get_sessions())
        )
        if len(active_sessions) > 0:
            return active_sessions[0]
        else:
            return manager.get_current_session()

    async def get_media_info(self):
        metadata = Metadata()
        current_session = await self.get_session()
        if current_session:
            playback_info = current_session.get_playback_info()
            play_status = playback_info.playback_status
            if play_status in [PlayStatus.PLAYING, PlayStatus.PAUSED]:
                metadata.status = play_status.name

                timeline_properties = current_session.get_timeline_properties()
                metadata.current = int(timeline_properties.position.total_seconds())
                metadata.total = int(timeline_properties.end_time.total_seconds())
                
                info = await current_session.try_get_media_properties_async()
                metadata.artist = info.artist
                metadata.title = info.title

                thumbnail = info.thumbnail
                if thumbnail:
                    metadata.thumbnail = await Thumbnail(thumbnail)
        return metadata
