from enum import Enum

from src.mail_agent.shared.models import LocalActionCapability


class NodesEnum(str, Enum):
    SEND_EMAIL = "send_email"
