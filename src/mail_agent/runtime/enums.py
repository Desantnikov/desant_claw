from enum import Enum


class EventType(str, Enum):
    HITL_RESPONSE = 'hitl_response'
    NEW_REQUEST = 'new_request'