from typing import TypedDict, List

class TranscriptItem(TypedDict):
    text: str
    start: float
    duration: float

transcript = List[TranscriptItem]

