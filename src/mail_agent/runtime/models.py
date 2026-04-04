from pydantic import BaseModel

from .enums import EventType


class Event(BaseModel):
    sender: str
    type: EventType
    content: dict
    decisions: list | None = None

    thread_id: str