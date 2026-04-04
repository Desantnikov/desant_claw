import re
import uuid

from .models import Event
from .enums import EventType


# TODO: split into separate classes for each input type
class EventFactory:
    EMAIL_REGEXP = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'

    @classmethod
    def from_email(cls, raw_email_data: dict) -> Event:
        content = cls._parse_content(raw_email_data=raw_email_data)
        sender_email = cls._parse_email(sender_string=raw_email_data["sender"])
        event_type = cls._identify_event_type(raw_email_data=raw_email_data)

        if event_type == EventType.HITL_RESPONSE:
            thread_id = cls._parse_thread_id(raw_email_data=raw_email_data)
        elif event_type == EventType.NEW_REQUEST:
            thread_id = cls._generate_new_thread_id()
        else:
            raise Exception("Invalid event type")

        return Event(
            sender=sender_email,
            type=event_type,
            content=content,
            thread_id=thread_id,
        )

    @classmethod
    def _parse_email(cls, sender_string: str) -> str:
        parsed_sender_email = re.search(cls.EMAIL_REGEXP, sender_string)
        parsed_sender_email = parsed_sender_email.group(0) if parsed_sender_email else None

        if parsed_sender_email is None:
            raise Exception("Invalid sender email")

        return parsed_sender_email

    @classmethod
    def _identify_event_type(cls, raw_email_data: dict) -> EventType:
        if 'HITL_RESPONSE' in raw_email_data['subject']:
            return EventType.HITL_RESPONSE
        return EventType.NEW_REQUEST

    @classmethod
    def _parse_content(cls, raw_email_data: dict) -> dict:
        return {
            "snippet": raw_email_data["snippet"],
            "body": raw_email_data["body"],
            "subject": raw_email_data["subject"],
            "sender": cls._parse_email(sender_string=raw_email_data["sender"]),
        }

    @classmethod
    def _parse_thread_id(cls, raw_email_data: dict) -> str:
        return raw_email_data['snippet']

    @staticmethod
    def _generate_new_thread_id() -> str:
        return str(uuid.uuid4())