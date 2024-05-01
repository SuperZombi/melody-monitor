from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlayStatus
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from dataclasses import dataclass
from abc import ABC, abstractmethod
import base64


##############################################


class Setting:
    def __init__(self, name, label, type, dft_value=None, promt="", values=None, min=None):
        self.name = name
        self.label = label
        if type in ["str", "int"]:
            self.type = type
        else:
            raise ValueError(f"Type «{type}» is not supported")
        if values and len(values) > 0:
            self.values = SettingsManager([Setting(type=self.type, **i) for i in values])
        else:
            self.values = None
        
        self.dft_value = dft_value
        self.value = dft_value
        self.promt = promt
        self.min = min

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        if type(new_value).__name__ != self.type and new_value != None:
            raise TypeError(f"{type(new_value).__name__}({new_value}) is not <{self.type}>")

        if self.values:
            if not hasattr(self.values, new_value):
                raise ValueError(f"<{self.name}>: «{new_value}» is not in {list(self.values.json().keys())}")

        self._value = new_value if new_value else self.dft_value
            

    @property
    def metadata(self):
        return {
            "name": self.name,
            "label": self.label,
            "type": self.type,
            "value": self.value,
            **({"promt": self.promt} if self.promt != "" else {}),
            **({"values": self.values.metadata} if self.values is not None else {}),
            **({"dft_value": self.dft_value} if self.dft_value is not None else {}),
            **({"min": self.min} if self.min is not None else {})
        }

    def __str__(self): return f"{self.name}={self.value}"
    def __repr__(self): return str(self)


class SettingsManager():
    def __init__(self, template):
        self.template = template
        for i in template:
            setattr(self, i.name, i)

    def load_settings(self, data):
        for k,v in data.items():
            if hasattr(self, k):
                obj = getattr(self, k)
                obj.value = v

    def set(self, name, new_value):
        getattr(self, name).value = new_value
    def get(self, name):
        return getattr(self, name).value

    def json(self, unique=False):
        if unique:
            return {obj.name: obj.value for obj in self.template if obj.dft_value != obj.value}
        else:
            return {obj.name: obj.value for obj in self.template}

    @property
    def metadata(self):
        return list(i.metadata for i in self.template)


##############################################


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
